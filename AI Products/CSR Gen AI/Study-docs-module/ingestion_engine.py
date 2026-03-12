import base64
import json
import logging
import os
import re
import sys
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv
from mistralai import Mistral
from google import genai
from google.genai import types

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

GEMINI_MODEL = "gemini-2.5-flash"
MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 5

NETWORK_ERRORS = (
    httpx.ConnectError,
    httpx.TimeoutException,
    httpx.RemoteProtocolError,
    ConnectionError,
    OSError,
    TimeoutError,
)


def _retry_on_network_error(func, *args, **kwargs):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return func(*args, **kwargs)
        except NETWORK_ERRORS as e:
            if attempt == MAX_RETRIES:
                logger.error(
                    "All %d retries exhausted. Last error: %s",
                    MAX_RETRIES, e,
                )
                raise
            wait = RETRY_BACKOFF_BASE * attempt
            logger.warning(
                "Network error (attempt %d/%d): %s. Retrying in %ds.",
                attempt, MAX_RETRIES, e, wait,
            )
            time.sleep(wait)


TREE_INDEX_PROMPT = """\
You are a document indexing specialist. Analyze the following Markdown text \
extracted from a regulatory/clinical document and produce a hierarchical \
JSON tree index.

The output must be a JSON array of node objects. Each node must have:
- "node_id": a unique string identifier (e.g., "protocol_1.1", "synopsis_2.3")
- "title": the heading or topic title
- "level": integer depth (1 = top-level section, 2 = subsection, etc.)
- "start_page": the approximate page number where this section starts \
  (based on page break markers in the text, e.g., "--- Page X ---")
- "end_page": the approximate page number where this section ends
- "summary": a 1-2 sentence summary of the content in this section
- "children": an array of child node objects (same structure), or empty array

Produce the tree by identifying all headings, sections, and subsections \
in the document. Preserve the document's hierarchy faithfully."""


class StudyIngestionEngine:

    def __init__(
        self,
        input_dir=None,
        ocr_output_dir=None,
        study_data_dir=None,
    ):
        base = Path(__file__).resolve().parent
        self.input_dir = Path(input_dir) if input_dir else base / "Input-docs"
        self.ocr_output_dir = (
            Path(ocr_output_dir) if ocr_output_dir else base / "ocr-output"
        )
        self.study_data_dir = (
            Path(study_data_dir) if study_data_dir else base / "study_data"
        )
        self.ocr_output_dir.mkdir(exist_ok=True)
        self.study_data_dir.mkdir(exist_ok=True)

        mistral_key = os.getenv("MISTRAL_API_KEY")
        if not mistral_key:
            raise EnvironmentError("MISTRAL_API_KEY is not set.")
        self.mistral_client = Mistral(
            api_key=mistral_key,
            timeout_ms=60000,
        )

        google_key = os.getenv("GOOGLE_API_KEY")
        if not google_key:
            raise EnvironmentError("GOOGLE_API_KEY is not set.")
        self.gemini_client = genai.Client(api_key=google_key)

        logger.info("StudyIngestionEngine initialized.")

    def _run_mistral_ocr(self, pdf_path):
        logger.info("Running Mistral OCR on %s.", pdf_path.name)
        try:
            with open(pdf_path, "rb") as f:
                base64_pdf = base64.b64encode(f.read()).decode("utf-8")

            ocr_response = _retry_on_network_error(
                self.mistral_client.ocr.process,
                model="mistral-ocr-latest",
                document={
                    "type": "document_url",
                    "document_url": f"data:application/pdf;base64,{base64_pdf}",
                },
                table_format="html",
                include_image_base64=True,
            )

            pages_data = []
            markdown_parts = []
            for idx, page in enumerate(ocr_response.pages):
                markdown_parts.append(f"--- Page {idx + 1} ---")
                markdown_parts.append(page.markdown)

                page_tables = []
                if hasattr(page, "tables") and page.tables:
                    for t_idx, table in enumerate(page.tables):
                        table_html = table if isinstance(table, str) else str(table)
                        page_tables.append({
                            "table_index": t_idx,
                            "html": table_html,
                        })

                page_images = []
                if hasattr(page, "images") and page.images:
                    for i_idx, image in enumerate(page.images):
                        image_b64 = image if isinstance(image, str) else str(image)
                        page_images.append({
                            "image_index": i_idx,
                            "base64": image_b64,
                        })

                pages_data.append({
                    "page_index": idx,
                    "markdown": page.markdown,
                    "tables": page_tables,
                    "images": page_images,
                })

            full_markdown = "\n\n".join(markdown_parts)
            stem = pdf_path.stem

            md_path = self.ocr_output_dir / f"{stem}.md"
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(full_markdown)
            logger.info("Saved OCR markdown to %s.", md_path)

            pages_json_path = self.ocr_output_dir / f"{stem}_pages.json"
            with open(pages_json_path, "w", encoding="utf-8") as f:
                json.dump(pages_data, f, indent=2, ensure_ascii=False)
            logger.info("Saved pages JSON to %s.", pages_json_path)

            return full_markdown, pages_data

        except Exception:
            logger.error(
                "Mistral OCR failed for %s.", pdf_path.name, exc_info=True
            )
            raise

    def _cache_tables_from_tlf(self, pages_json_path):
        logger.info("Extracting tables from TLF: %s.", pages_json_path.name)
        try:
            with open(pages_json_path, "r", encoding="utf-8") as f:
                pages = json.load(f)
        except (IOError, json.JSONDecodeError):
            logger.error(
                "Failed to read %s.", pages_json_path, exc_info=True
            )
            return []

        tables = []
        stem = pages_json_path.stem.replace("_pages", "")

        # Priority 1: Extract HTML tables from OCR (new approach)
        for page in pages:
            page_idx = page.get("page_index", 0)
            page_tables = page.get("tables", [])
            for t_entry in page_tables:
                t_idx = t_entry.get("table_index", 0)
                html_content = t_entry.get("html", "")
                if not html_content:
                    continue
                table_id = (
                    f"{stem}_page{page_idx + 1}_html_table{t_idx + 1}"
                )
                # Try to extract a title from the HTML or nearby markdown
                title = self._extract_table_title_from_context(
                    page.get("markdown", ""), t_idx, page_idx
                )
                tables.append({
                    "table_id": table_id,
                    "title": title,
                    "source_document": stem,
                    "source_page": page_idx + 1,
                    "html_content": html_content,
                    "markdown_content": html_content,
                })

        if tables:
            logger.info(
                "Extracted %d HTML tables from %s.", len(tables), stem
            )
            return tables

        # Priority 2: Extract pipe-delimited markdown tables (legacy)
        pipe_pattern = re.compile(
            r"^(\|.+\|)\n(\|[-:| ]+\|)\n((?:\|.+\|\n?)+)",
            re.MULTILINE,
        )
        title_pattern = re.compile(
            r"((?:Table|Figure)\s+\d+[a-zA-Z]?)\.\s*(.+?)(?=\n\[tbl-|\n\n(?:Table|Figure)\s+\d|\Z)",
            re.DOTALL,
        )
        section_title_pattern = re.compile(
            r"#*\s*(\d+\.\d+\.?)\s+(.+?)(?=\n\[tbl-|\n\n#|\Z)",
            re.DOTALL,
        )

        for page in pages:
            page_idx = page.get("page_index", 0)
            md = page.get("markdown", "")
            for match_idx, match in enumerate(pipe_pattern.finditer(md)):
                header_line = match.group(1).strip()
                full_table = match.group(0).strip()
                cols = [
                    c.strip()
                    for c in header_line.split("|")
                    if c.strip()
                ]
                table_id = (
                    f"{stem}_page{page_idx + 1}_table{match_idx + 1}"
                )
                tables.append({
                    "table_id": table_id,
                    "title": " | ".join(cols[:3]),
                    "source_document": stem,
                    "source_page": page_idx + 1,
                    "markdown_content": full_table,
                })

        if not tables:
            logger.info(
                "No pipe tables in %s. Parsing table titles.", stem,
            )
            seen = {}
            for page in pages:
                page_idx = page.get("page_index", 0)
                md = page.get("markdown", "")
                has_tbl_ref = "[tbl-" in md
                for m in title_pattern.finditer(md):
                    table_num = m.group(1).strip()
                    raw_title = re.sub(r"\s+", " ", m.group(2).strip())
                    raw_title = raw_title.rstrip(".")
                    table_id = f"{stem}_{table_num.replace(' ', '_')}"
                    if table_id in seen:
                        continue
                    seen[table_id] = True
                    tables.append({
                        "table_id": table_id,
                        "title": f"{table_num}. {raw_title}",
                        "source_document": stem,
                        "source_page": page_idx + 1,
                        "markdown_content": (
                            f"**{table_num}. {raw_title}**\n\n"
                            "_Table data is in the source TLF "
                            "document. Use reasoning_search to "
                            "retrieve related numerical data._"
                        ),
                    })
                if not tables and has_tbl_ref:
                    for m in section_title_pattern.finditer(md):
                        sec_num = m.group(1).strip()
                        raw_title = re.sub(
                            r"\s+", " ", m.group(2).strip()
                        )
                        raw_title = raw_title.rstrip(".")
                        table_id = (
                            f"{stem}_Section_{sec_num.replace('.', '_')}"
                        )
                        if table_id in seen:
                            continue
                        seen[table_id] = True
                        tables.append({
                            "table_id": table_id,
                            "title": f"Section {sec_num} {raw_title}",
                            "source_document": stem,
                            "source_page": page_idx + 1,
                            "markdown_content": (
                                f"**Section {sec_num} {raw_title}**"
                                "\n\n_Table data is in the source "
                                "TLF document. Use reasoning_search "
                                "to retrieve related numerical "
                                "data._"
                            ),
                        })

        logger.info("Extracted %d tables from %s.", len(tables), stem)
        return tables

    def _extract_table_title_from_context(self, markdown, table_idx, page_idx):
        """Extract a table title from the surrounding markdown context."""
        title_pattern = re.compile(
            r"((?:Table|Figure)\s+\d+[a-zA-Z]?)\.\s*(.+?)(?:\n|$)",
        )
        matches = list(title_pattern.finditer(markdown))
        if table_idx < len(matches):
            m = matches[table_idx]
            table_num = m.group(1).strip()
            raw_title = re.sub(r"\s+", " ", m.group(2).strip()).rstrip(".")
            return f"{table_num}. {raw_title}"
        return f"Table on page {page_idx + 1} (table {table_idx + 1})"

    def _build_tree_index(self, md_path):
        logger.info("Building tree index for %s.", md_path.name)
        try:
            with open(md_path, "r", encoding="utf-8") as f:
                content = f.read()
        except IOError:
            logger.error("Failed to read %s.", md_path, exc_info=True)
            raise

        # Truncate very large documents to avoid Gemini timeouts
        max_chars = 150_000
        if len(content) > max_chars:
            logger.warning(
                "Truncating %s from %d to %d chars for tree index.",
                md_path.name, len(content), max_chars,
            )
            content = content[:max_chars]

        try:
            response = _retry_on_network_error(
                self.gemini_client.models.generate_content,
                model=GEMINI_MODEL,
                contents=[content],
                config=types.GenerateContentConfig(
                    system_instruction=TREE_INDEX_PROMPT,
                    response_mime_type="application/json",
                ),
            )
            tree = json.loads(response.text)
        except json.JSONDecodeError:
            logger.error(
                "Gemini returned invalid JSON for %s.",
                md_path.name,
                exc_info=True,
            )
            raise
        except Exception:
            logger.error(
                "Tree index generation failed for %s.",
                md_path.name,
                exc_info=True,
            )
            raise

        stem = md_path.stem
        tree_path = self.study_data_dir / f"{stem}_tree.json"
        with open(tree_path, "w", encoding="utf-8") as f:
            json.dump(tree, f, indent=2, ensure_ascii=False)
        logger.info("Tree index saved to %s.", tree_path)
        return tree

    def run_ingestion(self):
        logger.info("Starting study document ingestion.")

        pdf_files = sorted(self.input_dir.glob("*.pdf"))
        if not pdf_files:
            logger.warning("No PDF files found in %s.", self.input_dir)
            return

        logger.info("Found %d PDF file(s) to process.", len(pdf_files))

        for pdf_path in pdf_files:
            stem = pdf_path.stem
            md_path = self.ocr_output_dir / f"{stem}.md"
            pages_json_path = self.ocr_output_dir / f"{stem}_pages.json"

            if md_path.exists() and pages_json_path.exists():
                logger.info(
                    "OCR output already exists for %s. Skipping OCR.",
                    pdf_path.name,
                )
            else:
                try:
                    self._run_mistral_ocr(pdf_path)
                except Exception:
                    logger.error(
                        "Skipping %s due to OCR failure.", pdf_path.name
                    )
                    continue

        tables_path = self.study_data_dir / "tables.json"
        existing_tables = {}
        if tables_path.exists():
            try:
                with open(tables_path, "r", encoding="utf-8") as f:
                    existing_list = json.load(f)
                existing_tables = {
                    t["table_id"]: t for t in existing_list
                }
            except (IOError, json.JSONDecodeError):
                logger.warning("Could not read existing tables.json.")

        master_table_list = list(existing_tables.values())

        for pages_json in sorted(self.ocr_output_dir.glob("*_pages.json")):
            stem = pages_json.stem.replace("_pages", "")
            stem_lower = stem.lower()
            is_tlf = "tlf" in stem_lower or "tfl" in stem_lower

            if is_tlf:
                already_cached = any(
                    t["source_document"] == stem
                    for t in master_table_list
                )
                if already_cached:
                    logger.info(
                        "Tables already cached for TLF %s. Skipping.", stem
                    )
                    continue
                new_tables = self._cache_tables_from_tlf(pages_json)
                master_table_list.extend(new_tables)

        if master_table_list:
            with open(tables_path, "w", encoding="utf-8") as f:
                json.dump(master_table_list, f, indent=2, ensure_ascii=False)
            logger.info(
                "Saved %d total tables to %s.",
                len(master_table_list),
                tables_path,
            )

        for md_file in sorted(self.ocr_output_dir.glob("*.md")):
            stem = md_file.stem
            stem_lower = stem.lower()
            if "tlf" in stem_lower or "tfl" in stem_lower:
                logger.info(
                    "Skipping tree index for TLF document %s.", stem
                )
                continue

            tree_path = self.study_data_dir / f"{stem}_tree.json"
            if tree_path.exists():
                logger.info(
                    "Tree index already exists for %s. Skipping.", stem
                )
                continue

            try:
                self._build_tree_index(md_file)
            except Exception:
                logger.error(
                    "Skipping tree index for %s due to error.", stem
                )

        logger.info("Study document ingestion complete.")


if __name__ == "__main__":
    engine = StudyIngestionEngine()
    engine.run_ingestion()
