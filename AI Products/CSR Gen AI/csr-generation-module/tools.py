import json
import logging
import os
import re
from pathlib import Path

from google import genai
from google.genai import types

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
STUDY_DATA_DIR = BASE_DIR / "Study-docs-module" / "study_data"
OCR_OUTPUT_DIR = BASE_DIR / "Study-docs-module" / "ocr-output"

GEMINI_MODEL = "gemini-2.5-pro"


def _get_gemini_client():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise EnvironmentError("GOOGLE_API_KEY is not set.")
    return genai.Client(api_key=api_key)


def reasoning_search(question: str) -> str:
    """Two-hop reasoning search over study documents.

    Hop 1 uses Gemini to identify the most relevant sections from tree
    indexes. Hop 2 retrieves the actual text from those sections.

    Args:
        question: The research question to answer from source documents.

    Returns:
        Concatenated relevant text extracted from source documents.
    """
    tree_files = sorted(STUDY_DATA_DIR.glob("*_tree.json"))
    if not tree_files:
        logger.warning("No tree index files found in %s.", STUDY_DATA_DIR)
        return "No study data indexes available."

    trees = {}
    for tf in tree_files:
        try:
            with open(tf, "r", encoding="utf-8") as f:
                trees[tf.stem] = json.load(f)
        except (IOError, json.JSONDecodeError):
            logger.error("Failed to load tree index %s.", tf, exc_info=True)

    if not trees:
        return "Failed to load any tree indexes."

    logger.info(
        "[CHUNK LOG] reasoning_search called | question=%r | "
        "tree_indexes_available=%s",
        question,
        list(trees.keys()),
    )

    hop1_prompt = (
        "You are a document retrieval specialist. Given the following "
        "question and document tree indexes, identify the most relevant "
        "sections to answer the question.\n\n"
        f"Question: {question}\n\n"
        "Tree Indexes:\n"
        f"{json.dumps(trees, indent=1)}\n\n"
        "Return a JSON array of objects, each with:\n"
        '- "source": the tree index name (without _tree suffix)\n'
        '- "node_id": the node_id of the relevant section\n'
        '- "start_page": start page number\n'
        '- "end_page": end page number\n'
        "Return at most 5 most relevant nodes."
    )

    try:
        client = _get_gemini_client()
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[hop1_prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2,
            ),
        )
        relevant_nodes = json.loads(response.text)
    except Exception:
        logger.error("Hop 1 reasoning search failed.", exc_info=True)
        return "Reasoning search failed at hop 1."

    logger.info(
        "[CHUNK LOG] Hop 1 selected %d node(s):", len(relevant_nodes)
    )
    for i, node in enumerate(relevant_nodes, 1):
        logger.info(
            "[CHUNK LOG]   Node %d: source=%r | node_id=%r | pages=%s-%s",
            i,
            node.get("source", ""),
            node.get("node_id", ""),
            node.get("start_page", "?"),
            node.get("end_page", "?"),
        )

    retrieved_parts = []
    for node in relevant_nodes:
        source = node.get("source", "")
        node_id = node.get("node_id", "")
        start_page = node.get("start_page", 1)
        end_page = node.get("end_page", start_page)
        md_path = OCR_OUTPUT_DIR / f"{source}.md"
        if not md_path.exists():
            logger.warning(
                "[CHUNK LOG] Source file not found: %s (node_id=%r)",
                md_path,
                node_id,
            )
            continue

        try:
            with open(md_path, "r", encoding="utf-8") as f:
                full_text = f.read()
        except IOError:
            logger.error("Failed to read %s.", md_path, exc_info=True)
            continue

        page_pattern = re.compile(r"--- Page (\d+) ---")
        pages = page_pattern.split(full_text)

        extracted = []
        i = 1
        while i < len(pages) - 1:
            page_num = int(pages[i])
            page_content = pages[i + 1]
            if start_page <= page_num <= end_page:
                extracted.append(
                    f"[{source} Page {page_num}]\n{page_content.strip()}"
                )
            i += 2

        if extracted:
            total_chars = sum(len(p) for p in extracted)
            logger.info(
                "[CHUNK LOG] Hop 2 extracted %d page(s) from "
                "source=%r node_id=%r (pages %s-%s) | "
                "total_chars=%d | preview=%r",
                len(extracted),
                source,
                node_id,
                start_page,
                end_page,
                total_chars,
                extracted[0][:120],
            )
            retrieved_parts.extend(extracted)
        else:
            logger.warning(
                "[CHUNK LOG] No pages extracted from source=%r "
                "node_id=%r (pages %s-%s) — pages not found in OCR output.",
                source,
                node_id,
                start_page,
                end_page,
            )

    if not retrieved_parts:
        logger.warning(
            "[CHUNK LOG] reasoning_search returned empty — "
            "no content found for question=%r",
            question,
        )
        return "No relevant content found for the given question."

    logger.info(
        "[CHUNK LOG] reasoning_search complete | question=%r | "
        "total_chunks_returned=%d | total_chars=%d",
        question,
        len(retrieved_parts),
        sum(len(p) for p in retrieved_parts),
    )
    return "\n\n---\n\n".join(retrieved_parts)


def _load_tables():
    tables_path = STUDY_DATA_DIR / "tables.json"
    if not tables_path.exists():
        logger.error("tables.json not found at %s.", tables_path)
        return None
    try:
        with open(tables_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError):
        logger.error("Failed to load tables.json.", exc_info=True)
        return None


_STOP_WORDS = {
    "a", "an", "the", "of", "in", "for", "and", "or", "to", "by",
    "at", "from", "with", "on", "is", "are", "was", "were", "that",
    "this", "as", "example", "table", "figure", "annex", "summary",
}


def _keyword_score(query_lower, title_lower):
    keywords = [
        w for w in re.split(r"[\s\-:.,;()/]+", query_lower)
        if w and w not in _STOP_WORDS and len(w) > 2
    ]
    if not keywords:
        return 0
    matched = sum(1 for kw in keywords if kw in title_lower)
    return matched / len(keywords)


def get_table(table_title_or_id: str) -> str:
    """Retrieve a specific table by its title, keywords, or unique ID.

    Searches the cached tables.json for a matching table using exact
    match, substring match, and keyword-based fuzzy matching.

    Args:
        table_title_or_id: A descriptive title, keywords, or table ID.

    Returns:
        The markdown content of the matching table, or an error message
        with a list of available tables to help find the right one.
    """
    tables = _load_tables()
    if tables is None:
        return "Error: tables.json not found. Run ingestion first."

    query_lower = table_title_or_id.lower()

    for table in tables:
        if table.get("table_id", "").lower() == query_lower:
            logger.info("Found table by ID: %s.", table["table_id"])
            return table.get("markdown_content", "")

    for table in tables:
        if query_lower in table.get("title", "").lower():
            logger.info("Found table by title match: %s.", table["table_id"])
            return table.get("markdown_content", "")

    for table in tables:
        if query_lower in table.get("table_id", "").lower():
            logger.info(
                "Found table by partial ID match: %s.", table["table_id"]
            )
            return table.get("markdown_content", "")

    scored = []
    for table in tables:
        title_lower = table.get("title", "").lower()
        score = _keyword_score(query_lower, title_lower)
        if score > 0.3:
            scored.append((score, table))
    scored.sort(key=lambda x: x[0], reverse=True)

    if scored:
        best = scored[0][1]
        logger.info(
            "Found table by keyword match: %s (score %.2f).",
            best["table_id"], scored[0][0],
        )
        result = best.get("markdown_content", "")
        if len(scored) > 1:
            others = ", ".join(
                f'"{s[1]["title"][:60]}"' for s in scored[1:4]
            )
            result += f"\n\n_Other possible matches: {others}_"
        return result

    available = "\n".join(
        f'- "{t["title"][:80]}"' for t in tables[:20]
    )
    logger.warning("Table not found: %s.", table_title_or_id)
    return (
        f"Error: Table '{table_title_or_id}' not found.\n\n"
        f"Available tables ({len(tables)} total):\n{available}"
    )


def list_tables() -> str:
    """List all available tables from the study data.

    Returns a formatted list of all table titles and IDs that can
    be retrieved using the get_table tool.

    Returns:
        A formatted list of available tables.
    """
    tables = _load_tables()
    if tables is None:
        return "Error: tables.json not found. Run ingestion first."

    if not tables:
        return "No tables available in tables.json."

    lines = [f"Available tables ({len(tables)} total):\n"]
    for t in tables:
        lines.append(
            f'- ID: "{t["table_id"]}" | '
            f'Title: "{t["title"][:100]}" | '
            f'Page: {t.get("source_page", "N/A")}'
        )
    return "\n".join(lines)
