import json
import logging
import re
from pathlib import Path

import pypandoc

logger = logging.getLogger(__name__)

MODULE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = MODULE_DIR / "output"
TEMPLATE_PATH = MODULE_DIR / "templates" / "csr_template.tex"

SECTION_ORDER = [
    "Section_1",
    "Section_2",
    "Section_5",
    "Section_6",
    "Section_7",
    "Section_8",
    "Section_9",
    "Section_10",
    "Section_11",
    "Section_12",
    "Section_13",
    "Section_14",
    "Section_15",
    "Section_16",
]

ABBREVIATION_MAP = {
    "ADR": (
        "Adverse Drug Reaction",
        "An unfavourable and unintended response to a medicinal product where a causal relationship is a reasonable possibility.",
    ),
    "AE": (
        "Adverse Event",
        "Any unfavourable medical occurrence in a participant administered an investigational product, regardless of causal relationship.",
    ),
    "ANCOVA": (
        "Analysis of Covariance",
        "A statistical method combining ANOVA and regression to compare group means while controlling for covariates.",
    ),
    "BMI": (
        "Body Mass Index",
        "A measure of body fat based on weight in kilograms divided by height in metres squared.",
    ),
    "BNT162b2": (
        "BioNTech COVID-19 mRNA Vaccine",
        "An RNA-based vaccine encoding the SARS-CoV-2 prefusion spike glycoprotein, formulated in lipid nanoparticles.",
    ),
    "CDC": (
        "Centers for Disease Control and Prevention",
        "United States federal public health agency.",
    ),
    "CI": (
        "Confidence Interval",
        "A range of values within which the true population parameter is expected to fall at a specified probability level.",
    ),
    "CIOMS": (
        "Council for International Organizations of Medical Sciences",
        "An international body providing guidance on health research ethics and drug safety.",
    ),
    "COVID-19": (
        "Coronavirus Disease 2019",
        "The infectious disease caused by the SARS-CoV-2 virus.",
    ),
    "CRF": (
        "Case Report Form",
        "A document used to record data for each study participant as defined by the protocol.",
    ),
    "CRO": (
        "Contract Research Organisation",
        "An organisation contracted by the sponsor to perform one or more trial-related duties.",
    ),
    "CSR": (
        "Clinical Study Report",
        "An integrated full report of an individual clinical study of a therapeutic, prophylactic, or diagnostic agent.",
    ),
    "DMC": (
        "Data Monitoring Committee",
        "An independent committee that reviews accumulating data from an ongoing clinical trial to ensure participant safety.",
    ),
    "ECG": (
        "Electrocardiogram",
        "A recording of the electrical activity of the heart over a period of time.",
    ),
    "EUA": (
        "Emergency Use Authorization",
        "A regulatory mechanism to facilitate availability of medical countermeasures during public health emergencies.",
    ),
    "GCP": (
        "Good Clinical Practice",
        "An international ethical and scientific quality standard for designing, conducting, recording, and reporting clinical trials.",
    ),
    "GMT": (
        "Geometric Mean Titer",
        "A measure of central tendency for antibody titers, calculated as the antilog of the mean of log-transformed values.",
    ),
    "GMR": (
        "Geometric Mean Ratio",
        "The ratio of geometric mean titers between two groups, used to assess noninferiority of immune responses.",
    ),
    "ICD": (
        "Informed Consent Document",
        "A document that provides study participants with information about the trial to support their decision to participate.",
    ),
    "ICH": (
        "International Council for Harmonisation",
        "An organisation that brings together regulatory authorities and the pharmaceutical industry to harmonise guidelines.",
    ),
    "IEC": (
        "Independent Ethics Committee",
        "An independent body responsible for reviewing the ethics, safety, and scientific merit of a proposed clinical trial.",
    ),
    "IgG": (
        "Immunoglobulin G",
        "The most abundant antibody class in blood and extracellular fluid, providing long-term immune protection.",
    ),
    "IM": (
        "Intramuscular",
        "Administration of a substance into a muscle.",
    ),
    "IRB": (
        "Institutional Review Board",
        "A committee that reviews and monitors biomedical research involving human subjects to ensure ethical conduct.",
    ),
    "ITT": (
        "Intent-to-Treat",
        "An analysis population that includes all randomised participants regardless of protocol adherence.",
    ),
    "LNP": (
        "Lipid Nanoparticle",
        "A delivery system used to encapsulate and deliver mRNA vaccines into cells.",
    ),
    "MedDRA": (
        "Medical Dictionary for Regulatory Activities",
        "A standardised medical terminology used for regulatory communication and evaluation of medicinal products.",
    ),
    "mRNA": (
        "Messenger Ribonucleic Acid",
        "A molecule that carries genetic instructions for protein synthesis; the basis of the BNT162b2 vaccine technology.",
    ),
    "NAAT": (
        "Nucleic Acid Amplification Test",
        "A molecular diagnostic test that detects genetic material of a pathogen, such as PCR-based SARS-CoV-2 tests.",
    ),
    "PP": (
        "Per Protocol",
        "An analysis population that includes only participants who completed the study without major protocol deviations.",
    ),
    "QA": (
        "Quality Assurance",
        "A systematic process to determine whether trial-related activities and data comply with protocols, SOPs, and GCP.",
    ),
    "QC": (
        "Quality Control",
        "Operational techniques and procedures used to verify that data and processes meet quality requirements.",
    ),
    "RBD": (
        "Receptor-Binding Domain",
        "The portion of the SARS-CoV-2 spike protein that binds to the ACE2 receptor on human cells.",
    ),
    "SAE": (
        "Serious Adverse Event",
        "Any adverse event that results in death, is life-threatening, requires hospitalisation, or causes persistent disability.",
    ),
    "SAP": (
        "Statistical Analysis Plan",
        "A document describing the planned analyses for a clinical trial, including primary and secondary endpoints.",
    ),
    "SARS-CoV-2": (
        "Severe Acute Respiratory Syndrome Coronavirus 2",
        "The novel coronavirus that causes COVID-19.",
    ),
    "SOP": (
        "Standard Operating Procedure",
        "Detailed written instructions to achieve uniformity in the performance of a specific function.",
    ),
    "SUSAR": (
        "Suspected Unexpected Serious Adverse Reaction",
        "An adverse reaction that is both serious and unexpected, and where a causal relationship to the investigational product is suspected.",
    ),
    "TESS": (
        "Treatment Emergent Signs and Symptoms",
        "Signs and symptoms not present at baseline or that worsened during or after treatment.",
    ),
    "Th1": (
        "T Helper Type 1",
        "A subset of CD4+ T cells that promote cell-mediated immune responses.",
    ),
    "VE": (
        "Vaccine Efficacy",
        "A measure of the proportionate reduction in disease incidence among vaccinated compared to unvaccinated individuals.",
    ),
    "VOC": (
        "Variant of Concern",
        "A SARS-CoV-2 variant with mutations that may affect transmissibility, disease severity, or vaccine effectiveness.",
    ),
    "WHO": (
        "World Health Organization",
        "A specialised agency of the United Nations responsible for international public health.",
    ),
}


def compile_sections(output_dir=None, section_order=None):
    output_dir = Path(output_dir) if output_dir else OUTPUT_DIR
    section_order = section_order or SECTION_ORDER

    parts = []
    for section_key in section_order:
        md_path = output_dir / f"{section_key}.md"
        if not md_path.exists():
            logger.warning("Section file %s not found. Skipping.", md_path)
            continue
        try:
            with open(md_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
            if content:
                parts.append(content)
                logger.info("Included %s.", section_key)
        except IOError:
            logger.error("Failed to read %s.", md_path, exc_info=True)

    if not parts:
        logger.error("No section content found to compile.")
        return ""

    return "\n\n\\newpage\n\n".join(parts)


def generate_abbreviations_section(content):
    found = {}
    for abbr, entry in ABBREVIATION_MAP.items():
        full_form, definition = entry
        pattern = re.compile(r"\b" + re.escape(abbr) + r"\b")
        if pattern.search(content):
            found[abbr] = (full_form, definition)

    if not found:
        logger.info("No abbreviations detected in content.")
        return ""

    lines = ["# 4. List of Abbreviations and Definition of Terms", ""]
    lines.append("| Abbreviation | Definition/Context |")
    lines.append("|:---|:---|")
    for abbr in sorted(found.keys()):
        full_form, definition = found[abbr]
        lines.append(f"| {abbr} | {full_form} |")

    logger.info("Generated abbreviations section with %d entries.", len(found))
    return "\n".join(lines)


def generate_toc_section():
    lines = [
        "# 3. Table of Contents",
        "",
        "```{=latex}",
        "\\tableofcontents",
        "```",
    ]
    return "\n".join(lines)


def _escape_latex(text):
    """Escape special LaTeX characters in text."""
    for ch, rep in [('&', '\\&'), ('%', '\\%'), ('#', '\\#'), ('_', '\\_')]:
        text = text.replace(ch, rep)
    return text


def _collect_all_tables(body_content, output_dir=None):
    """Scan all sections for tables and assign global numbers 1..N.

    Returns list of dicts: {global_num, section, orig_id, title, label}
    """
    output_dir = Path(output_dir) if output_dir else OUTPUT_DIR
    all_tables = []

    # Collect in-text tables from sections (non-Section_14)
    for sec in SECTION_ORDER:
        if sec == "Section_14":
            continue
        md_path = output_dir / f"{sec}.md"
        if not md_path.exists() or md_path.stat().st_size == 0:
            continue
        with open(md_path, "r", encoding="utf-8") as f:
            content = f.read()
        for m in re.finditer(
            r'(?:^|\n)\s*(?:\*\*)?Table\s+(\d+(?:\.\d+)?)\s*[.:]\s*(?:\*\*)?\s*(.+?)(?:\n|$)',
            content,
        ):
            tbl_id = m.group(1)
            tbl_title = m.group(2).strip().rstrip('*').strip()
            label = f"tbl-{sec}-{tbl_id}"
            all_tables.append({
                "section": sec,
                "orig_id": tbl_id,
                "title": tbl_title,
                "label": label,
            })

    # Collect Section 14 tables from table_index.json
    index_path = output_dir / "table_index.json"
    if index_path.exists():
        with open(index_path, "r", encoding="utf-8") as f:
            s14_entries = json.load(f)
        for entry in s14_entries:
            all_tables.append({
                "section": "Section_14",
                "orig_id": entry["num"],
                "title": entry["title"],
                "label": entry["label"],
            })

    # Deduplicate (same title in same section = same table referenced multiple times)
    seen = set()
    deduped = []
    for t in all_tables:
        key = (t["section"], t["orig_id"], t["title"][:50])
        if key not in seen:
            seen.add(key)
            deduped.append(t)

    # Assign global numbers
    for i, t in enumerate(deduped, 1):
        t["global_num"] = i

    return deduped


def generate_tfl_index(body_content, output_dir=None):
    """Generate LIST OF IN-TEXT TABLES with global numbering and page refs.

    Uses LaTeX contentsline-style formatting to match the TOC visual style.
    """
    tables = _collect_all_tables(body_content, output_dir)
    if not tables:
        return "", tables

    # Split into in-text tables and Section 14 tables
    intext_tables = [t for t in tables if t["section"] != "Section_14"]
    s14_tables = [t for t in tables if t["section"] == "Section_14"]

    lines = [
        "# List of In-Text Tables",
        "",
        "```{=latex}",
        "\\makeatletter",
    ]
    for t in intext_tables:
        safe_title = _escape_latex(t["title"])
        safe_title = re.sub(r'\$[^$]*\$', '\\%', safe_title)
        entry_text = f"Table {t['global_num']}: {safe_title}"
        lines.append(
            f"\\contentsline{{section}}"
            f"{{\\numberline{{}}{entry_text}}}"
            f"{{\\pageref{{{t['label']}}}}}{{}}"
        )
    lines.append("\\makeatother")
    lines.append("```")
    return "\n".join(lines), tables


def _insert_table_labels(content, tables):
    """Insert LaTeX \\label commands before each table in section content.

    Also renumber tables to global numbering, including Section 14 tables.
    """
    for t in tables:
        orig_id = t["orig_id"]
        global_num = t["global_num"]
        label = t["label"]

        if t["section"] == "Section_14":
            # Section 14 keeps its original 14.1, 14.2, etc. numbering
            continue

        title_snippet = t["title"][:40]

        # Find "Table <orig_id>." or "Table <orig_id>:" and insert label before,
        # also renumber to global number
        pattern = re.compile(
            r'(\n\s*(?:\*\*)?)(Table\s+)'
            + re.escape(orig_id)
            + r'(\s*[.:]\s*(?:\*\*)?\s*'
            + re.escape(title_snippet[:20])
            + r')',
            re.IGNORECASE,
        )
        match = pattern.search(content)
        if match:
            label_block = (
                f"\n\n```{{=latex}}\n\\label{{{label}}}\n```\n"
            )
            replacement = (
                label_block
                + match.group(1)
                + match.group(2)
                + str(global_num)
                + match.group(3)
            )
            content = content[:match.start()] + replacement + content[match.end():]

    return content


def create_final_pdf(content, template_path=None, output_path=None):
    template_path = Path(template_path) if template_path else TEMPLATE_PATH
    output_path = (
        Path(output_path) if output_path
        else MODULE_DIR / "output" / "CSR.pdf"
    )

    if not template_path.exists():
        logger.error("LaTeX template not found at %s.", template_path)
        raise FileNotFoundError(f"Template not found: {template_path}")

    output_path.parent.mkdir(exist_ok=True)

    extra_args = [
        f"--template={template_path}",
        "--pdf-engine=xelatex",
        "--resource-path=.",
    ]

    try:
        pypandoc.convert_text(
            content,
            "pdf",
            format="markdown",
            outputfile=str(output_path),
            extra_args=extra_args,
        )
        logger.info("Final PDF created at %s.", output_path)
    except Exception:
        logger.error("PDF generation failed.", exc_info=True)
        raise


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger.info("Compiling CSR sections.")
    body_content = compile_sections()
    if not body_content:
        logger.error("No content to publish. Aborting.")
        return

    logger.info("Generating abbreviations section.")
    abbrev_section = generate_abbreviations_section(body_content)

    logger.info("Generating table of contents placeholder.")
    toc_section = generate_toc_section()

    logger.info("Collecting all tables and generating index.")
    tfl_index, all_tables = generate_tfl_index(body_content)

    # Insert labels and renumber tables in body content
    logger.info("Inserting table labels and renumbering.")
    body_content = _insert_table_labels(body_content, all_tables)

    # --- Assemble document ---
    # Order: Title Page -> Synopsis -> TOC -> List of Tables -> Abbreviations -> rest
    s2_match = re.search(r"\n\\newpage\s*\n+(?=# 2\. Synopsis)", body_content)
    s5_match = re.search(r"\n\\newpage\s*\n+(?=# 5\. )", body_content)

    if s2_match and s5_match:
        title_page = body_content[: s2_match.start()]
        synopsis = body_content[s2_match.end() : s5_match.start()]
        rest = body_content[s5_match.end() :]

        # Insert \newpage before tables in Synopsis
        synopsis = re.sub(
            r'\n(Table \d+\.)',
            r'\n\\newpage\n\n\1',
            synopsis,
            count=1,
        )

        tfl_part = ""
        if tfl_index:
            tfl_part = "\n\n\\newpage\n\n" + tfl_index

        full_content = (
            title_page
            + "\n\n\\newpage\n\n"
            + synopsis.strip()
            + "\n\n\\newpage\n\n"
            + toc_section
            + tfl_part
            + "\n\n\\newpage\n\n"
            + abbrev_section
            + "\n\n\\newpage\n\n"
            + rest.lstrip("\n")
        )
    else:
        # Fallback: just prepend TOC and abbreviations
        full_content = (
            toc_section
            + "\n\n\\newpage\n\n"
            + abbrev_section
            + "\n\n\\newpage\n\n"
            + body_content
        )

    # Remove \newpage before subsection headings (## and ###)
    # Only main sections (#) should start on new pages
    full_content = re.sub(
        r"\\newpage\s*\n\s*\n(##[^#])",
        r"\1",
        full_content,
    )
    # Also remove \newpage before ## N.N subsection headings (e.g., ## 10.1, ## 13.2)
    full_content = re.sub(
        r"\\newpage\s*\n\s*\n(## \d+\.\d+)",
        r"\1",
        full_content,
    )

    logger.info("Creating final PDF.")
    create_final_pdf(full_content)
    logger.info("CSR publishing complete.")


if __name__ == "__main__":
    main()
