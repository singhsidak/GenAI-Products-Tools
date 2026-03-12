import json
import logging
from typing import List

from pydantic import BaseModel, Field
from google.genai import types

from utils import (
    get_gemini_client,
    get_mistral_client,
    read_pdf_files,
    save_ocr_markdown,
    write_json_output,
)

logger = logging.getLogger(__name__)

GEMINI_MODEL = "gemini-2.5-flash"


class ClinicalDefinition(BaseModel):
    term: str = Field(
        description="The clinical or regulatory term or abbreviation "
        "(e.g., AE, SAE, SUSAR, TESS, ICH, GCP)."
    )
    definition: str = Field(
        description="The exact definition as stated or directly implied "
        "by the source regulatory document. Do not paraphrase beyond "
        "what the text supports."
    )


class DataDependency(BaseModel):
    reference_id: str = Field(
        description="The identifier of the referenced item exactly as it "
        "appears in the guideline (e.g., 'Appendix 16.1.1', "
        "'Section 14.3.2', 'Annex IVa')."
    )
    title: str = Field(
        description="The official title or name of the referenced item "
        "as stated in the source document (e.g., 'Protocol and "
        "protocol amendments', 'Listings of Deaths, Other Serious "
        "and Significant Adverse Events')."
    )
    content_summary: str = Field(
        description="A concise summary of what this referenced item "
        "contains or requires, extracted from the source document. "
        "This must provide enough context so a downstream agent "
        "can understand what data belongs here without needing to "
        "look up the original reference."
    )


class SectionSchema(BaseModel):
    section_key: str = Field(
        description="The section identifier, strictly one of: Section_1, "
        "Section_2, Section_3, ..., Section_16."
    )
    section_title: str = Field(
        description="The official ICH E3 section title exactly as defined "
        "in the guideline (e.g., 'Title Page', 'Synopsis')."
    )
    required_content: List[str] = Field(
        description="List of explicit instructions extracted from the "
        "regulatory text on what must be written in this section. "
        "Each item must be a direct requirement, not an interpretation."
    )
    data_dependencies: List[DataDependency] = Field(
        description="List of resolved references to appendices, tables, "
        "figures, or other sections that this section must reference. "
        "Each dependency must include the reference identifier, its "
        "official title, and a summary of its required content as "
        "described in the source document."
    )
    critical_safety_checks: List[str] = Field(
        description="Specific compliance and patient-safety verification "
        "checks for this section extracted from the regulatory text "
        "(e.g., 'Ensure all deaths have narratives', "
        "'Verify all SAEs are listed regardless of causality'). "
        "Only include checks explicitly required by the source document."
    )


class CSRKnowledgeBase(BaseModel):
    clinical_definitions: List[ClinicalDefinition] = Field(
        description="Strict medical and regulatory definitions extracted "
        "verbatim or near-verbatim from the source document. "
        "Includes abbreviations like AE, SAE, SUSAR, TESS, CIOMS, "
        "IEC, IRB, CRF, and any other defined terms."
    )
    global_writing_constraints: List[str] = Field(
        description="Rules governing the overall tone, objectivity, and "
        "data integrity of the CSR. Includes requirements such as: "
        "maintain objective non-promotional language, identify all "
        "estimated or derived values, distinguish protocol-planned vs "
        "post-hoc analyses, and preserve clear audit trails. "
        "Extract only constraints explicitly stated in the text."
    )
    forbidden_actions: List[str] = Field(
        description="Explicit prohibitions derived from the regulatory text "
        "that an AI or author must NOT do when generating CSR content. "
        "Examples: do not infer causality not established by the "
        "investigator, do not omit safety data regardless of perceived "
        "relevance, do not use JavaScript in PDFs, do not skip "
        "reporting of adverse events considered unrelated. "
        "Each item must trace to a specific guideline requirement."
    )
    formatting_rules: List[str] = Field(
        description="All technical formatting specifications extracted from "
        "the regulatory text: PDF version requirements, font sizes, "
        "font families, margin dimensions, page orientation, DPI for "
        "scanned images, bookmark and hyperlink requirements, file "
        "naming conventions, and color specifications."
    )
    sections: List[SectionSchema] = Field(
        description="A list of exactly 16 section objects, one for each "
        "ICH E3 CSR section (Section_1 through Section_16). Each object "
        "must include the section_key, official title, and extracted "
        "requirements. If the source document has no content for a "
        "section, provide the official title with empty lists."
    )


SYSTEM_PROMPT = """\
You are an expert ICH-GCP Regulatory Compliance Officer. Your sole task is to \
extract precise, auditable rules from the provided regulatory document text \
for writing a Clinical Study Report (CSR) per ICH E3 guidelines.

STRICT EXTRACTION RULES:
- Extract ONLY what is explicitly stated or directly required by the source text.
- Do NOT hallucinate, infer, or add requirements not present in the document.
- Do NOT paraphrase loosely; preserve the regulatory intent and specificity.
- Every extracted rule must be traceable to the source document.

For Clinical_Definitions: extract every medical/regulatory term that is \
defined or described in the text (AE, SAE, SUSAR, TESS, CIOMS, etc.) with \
their exact definitions.

For Global_Writing_Constraints: extract rules about tone (objective, \
non-promotional), data integrity (identifying derived/estimated values), \
audit trail requirements, and report structure mandates.

For Forbidden_Actions: derive explicit prohibitions from the regulatory text. \
If the text says "must include all adverse events whether or not considered \
drug related", the forbidden action is "Do not omit adverse events based on \
causality assessment." Frame each as a clear "Do not..." statement.

For Formatting_Rules: isolate every PDF specification, font requirement, \
margin dimension, page layout rule, bookmark/hyperlink requirement, scanning \
DPI, and file naming convention.

For Sections: use exactly keys Section_1 through Section_16 mapped to:
- Section 1: Title Page
- Section 2: Synopsis
- Section 3: Table of Contents
- Section 4: List of Abbreviations and Definition of Terms
- Section 5: Ethics
- Section 6: Investigators and Study Administrative Structure
- Section 7: Introduction
- Section 8: Study Objectives
- Section 9: Investigational Plan
- Section 10: Study Patients
- Section 11: Efficacy Evaluation
- Section 12: Safety Evaluation
- Section 13: Discussion and Overall Conclusions
- Section 14: Tables, Figures and Graphs
- Section 15: Reference List
- Section 16: Appendices

For each section extract: the official title, required content as a list of \
specific instructions, data dependencies, and critical safety checks.

CRITICAL for data_dependencies: Do NOT output bare reference strings like \
"Appendix 16.1.1". Instead, for every referenced appendix, table, figure, \
annex, or section, resolve it into a structured object containing:
- reference_id: the identifier (e.g., "Appendix 16.1.1")
- title: the official name from the source document (e.g., "Protocol and \
protocol amendments")
- content_summary: what the referenced item contains or requires, extracted \
from the source text, providing enough context so a downstream agent \
understands what data belongs there without needing the original document.

If the source text has no content for a section, return the title with \
empty lists."""


class GuidelinesProcessor:

    def __init__(self):
        self.mistral_client = get_mistral_client()
        self.gemini_client = get_gemini_client()

    def extract_text(self, pdf_path):
        logger.info("Extracting text from %s via Mistral OCR.", pdf_path.name)
        uploaded_file = None
        try:
            uploaded_file = self.mistral_client.files.upload(
                file={
                    "file_name": pdf_path.name,
                    "content": open(pdf_path, "rb"),
                },
                purpose="ocr",
            )
            signed_url = self.mistral_client.files.get_signed_url(
                file_id=uploaded_file.id
            )
            ocr_response = self.mistral_client.ocr.process(
                model="mistral-ocr-latest",
                document={
                    "type": "document_url",
                    "document_url": signed_url.url,
                },
                table_format="markdown",
                include_image_base64=False,
            )
            markdown_text = "\n\n".join(
                page.markdown for page in ocr_response.pages
            )
            logger.info(
                "Extracted %d pages from %s.",
                len(ocr_response.pages),
                pdf_path.name,
            )
            save_ocr_markdown(pdf_path.name, markdown_text)
            return markdown_text
        except Exception:
            logger.error(
                "Mistral OCR failed for %s.", pdf_path.name, exc_info=True
            )
            raise
        finally:
            if uploaded_file:
                try:
                    self.mistral_client.files.delete(file_id=uploaded_file.id)
                    logger.info(
                        "Deleted uploaded file %s from Mistral.",
                        uploaded_file.id,
                    )
                except Exception:
                    logger.warning(
                        "Failed to delete file %s from Mistral.",
                        uploaded_file.id,
                        exc_info=True,
                    )

    def transform_text(self, markdown_text):
        logger.info("Transforming extracted text via Gemini (%s).", GEMINI_MODEL)
        try:
            response = self.gemini_client.models.generate_content(
                model=GEMINI_MODEL,
                contents=[markdown_text],
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    response_mime_type="application/json",
                    response_schema=CSRKnowledgeBase,
                    temperature=0.3,
                ),
            )
            parsed = CSRKnowledgeBase.model_validate_json(response.text)
            logger.info("Gemini transformation and validation complete.")
            return parsed
        except Exception:
            logger.error("Gemini processing failed.", exc_info=True)
            raise

    @staticmethod
    def merge_results(results: list[CSRKnowledgeBase]) -> dict:
        seen_definitions = {}
        merged_constraints = []
        merged_forbidden = []
        merged_formatting = []
        merged_sections = {}

        for result in results:
            for defn in result.clinical_definitions:
                if defn.term not in seen_definitions:
                    seen_definitions[defn.term] = defn.definition

            merged_constraints.extend(result.global_writing_constraints)
            merged_forbidden.extend(result.forbidden_actions)
            merged_formatting.extend(result.formatting_rules)

            for section in result.sections:
                key = section.section_key
                if key not in merged_sections:
                    merged_sections[key] = {
                        "section_title": section.section_title,
                        "required_content": list(section.required_content),
                        "data_dependencies": {
                            dep.reference_id: dep.model_dump()
                            for dep in section.data_dependencies
                        },
                        "critical_safety_checks": list(
                            section.critical_safety_checks
                        ),
                    }
                else:
                    existing = merged_sections[key]
                    existing["required_content"].extend(
                        section.required_content
                    )
                    for dep in section.data_dependencies:
                        if dep.reference_id not in existing["data_dependencies"]:
                            existing["data_dependencies"][dep.reference_id] = (
                                dep.model_dump()
                            )
                    existing["critical_safety_checks"].extend(
                        section.critical_safety_checks
                    )

        for key in merged_sections:
            s = merged_sections[key]
            s["required_content"] = list(dict.fromkeys(s["required_content"]))
            s["data_dependencies"] = list(
                s["data_dependencies"].values()
            )
            s["critical_safety_checks"] = list(
                dict.fromkeys(s["critical_safety_checks"])
            )

        return {
            "Clinical_Definitions": [
                {"term": t, "definition": d}
                for t, d in seen_definitions.items()
            ],
            "Global_Writing_Constraints": list(
                dict.fromkeys(merged_constraints)
            ),
            "Forbidden_Actions": list(dict.fromkeys(merged_forbidden)),
            "Formatting_Rules": list(dict.fromkeys(merged_formatting)),
            "Sections": merged_sections,
        }

    def run(self):
        pdf_files = read_pdf_files()
        if not pdf_files:
            logger.info("No PDFs to process. Exiting.")
            return

        results = []
        for pdf_path in pdf_files:
            try:
                markdown_text = self.extract_text(pdf_path)
                rules = self.transform_text(markdown_text)
                results.append(rules)
            except Exception:
                logger.error(
                    "Skipping %s due to processing error.", pdf_path.name
                )

        if results:
            merged = self.merge_results(results)
            write_json_output(merged)
            logger.info(
                "Pipeline complete. Processed %d file(s).", len(results)
            )
        else:
            logger.warning("No files were successfully processed.")


if __name__ == "__main__":
    processor = GuidelinesProcessor()
    processor.run()
