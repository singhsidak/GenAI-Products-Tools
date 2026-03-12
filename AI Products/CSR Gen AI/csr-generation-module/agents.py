import json
import logging
from pathlib import Path

from google.adk.agents import Agent
from google.genai import types

from tools import reasoning_search, get_table, list_tables

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
GUIDELINES_PATH = BASE_DIR / "Guidelines-module" / "guidlines.json"
AGENT_MODEL = "gemini-2.5-pro"

SECTION_MAP = {
    "Section_1": "Title Page",
    "Section_2": "Synopsis",
    "Section_5": "Ethics",
    "Section_6": "Investigators and Study Administrative Structure",
    "Section_7": "Introduction",
    "Section_8": "Study Objectives",
    "Section_9": "Investigational Plan",
    "Section_10": "Study Patients",
    "Section_11": "Efficacy Evaluation",
    "Section_12": "Safety Evaluation",
    "Section_13": "Discussion and Overall Conclusions",
    "Section_14": "Tables, Figures and Graphs",
    "Section_15": "Reference List",
    "Section_16": "Appendices",
}


def _load_guidelines():
    try:
        with open(GUIDELINES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError):
        logger.error(
            "Failed to load guidelines from %s.", GUIDELINES_PATH,
            exc_info=True,
        )
        raise


def _build_section_instruction(guidelines, section_key):
    global_rules = guidelines.get("Global_Writing_Constraints", [])
    forbidden = guidelines.get("Forbidden_Actions", [])

    section_data = None
    sections = guidelines.get("Sections", {})
    if isinstance(sections, dict):
        section_data = sections.get(section_key)
    elif isinstance(sections, list):
        for s in sections:
            if s.get("section_key") == section_key:
                section_data = s
                break

    if not section_data:
        section_data = {
            "section_title": SECTION_MAP.get(section_key, section_key),
            "required_content": [],
            "data_dependencies": [],
            "critical_safety_checks": [],
        }

    title = section_data.get("section_title", section_key)
    required = section_data.get("required_content", [])
    dependencies = section_data.get("data_dependencies", [])
    safety_checks = section_data.get("critical_safety_checks", [])

    deps_text = ""
    if dependencies:
        dep_lines = []
        for dep in dependencies:
            if isinstance(dep, dict):
                ref = dep.get("reference_id", "")
                dep_title = dep.get("title", "")
                summary = dep.get("content_summary", "")
                dep_lines.append(
                    f"  - {ref}: {dep_title}\n    Content: {summary}"
                )
            else:
                dep_lines.append(f"  - {dep}")
        deps_text = (
            "\n\nDATA DEPENDENCIES (use reasoning_search or get_table "
            "to retrieve this data):\n" + "\n".join(dep_lines)
        )

    safety_text = ""
    if safety_checks:
        safety_text = (
            "\n\nCRITICAL SAFETY CHECKS (you MUST verify these):\n"
            + "\n".join(f"  - {c}" for c in safety_checks)
        )

    # Determine the correct heading level for the section number
    section_num = section_key.replace("Section_", "")
    heading_example = f"# {section_num}. {title}"

    instruction = (
        f"You are a regulatory medical writer generating {title} "
        f"({section_key}) of a Clinical Study Report (CSR).\n\n"
        "GLOBAL WRITING CONSTRAINTS (apply to ALL sections):\n"
        + "\n".join(f"  - {r}" for r in global_rules[:15])
        + "\n\nFORBIDDEN ACTIONS (you must NEVER do these):\n"
        + "\n".join(f"  - {f}" for f in forbidden[:15])
        + f"\n\nSECTION: {title}\n"
        "REQUIRED CONTENT (you must address each item):\n"
        + "\n".join(f"  {i+1}. {r}" for i, r in enumerate(required))
        + deps_text
        + safety_text
        + "\n\nINSTRUCTIONS:\n"
        "- FIRST call list_tables to see what tables are available "
        "in the study data before attempting to use get_table.\n"
        "- Use the reasoning_search tool to find relevant data from "
        "study source documents.\n"
        "- Use the get_table tool to retrieve pre-cached tables by "
        "title keywords or ID. IMPORTANT: Use keywords from the "
        "actual study (e.g., 'disposition', 'demographic', "
        "'adverse event', 'efficacy') rather than generic guideline "
        "template names (e.g., 'Annex IVa').\n"
        "- Output well-structured Markdown.\n"
        "- Do NOT include local file paths or source document names "
        "in the output.\n"
        "- Do NOT leave placeholders like [XX.X]%, [Number], [YY.Y], "
        "[TBD], or incomplete content. If exact data is unavailable, "
        "state findings narratively using whatever data you found.\n"
        "- Do NOT use stray characters like '*' after tables.\n"
        "- Number all tables sequentially within the section.\n"
        "- Use ONLY the standard ICH E3 section numbering. For "
        "example: '# 2. Synopsis', '## 8.1 Primary Objectives'. "
        "Do NOT prepend extra numbering layers (e.g., '4.1 1.1').\n"
        "- CRITICAL: Your output must contain ONLY the final polished "
        "section content in Markdown. Do NOT include any internal "
        "reasoning, planning notes, tool call commentary, or "
        "sentences describing what you searched for or found. "
        "No meta-commentary like 'The reasoning_search returned...', "
        "'I will now...', 'Let me try...', or 'Based on the tool "
        "output...'. Write as a regulatory medical writer, not as "
        "an AI assistant.\n"
        "- If table data is not available from get_table, construct "
        "the table from data found via reasoning_search. If no data "
        "exists, omit the table with a brief note.\n\n"
        "MARKDOWN FORMATTING RULES (STRICTLY FOLLOW):\n"
        f"- The main section heading MUST use a single '#': "
        f"'{heading_example}'\n"
        "- Subsections use '##' (e.g., '## 9.1 ...'), sub-subsections "
        "use '###' (e.g., '### 9.1.1 ...'). NEVER use '##' or '###' "
        "for the main section heading.\n"
        "- For bullet lists, ALWAYS use '- ' (dash + space). "
        "NEVER use '* ' (asterisk + space) for bullets, as it causes "
        "rendering issues in the final PDF.\n"
        "- For bold text use '**text**'. Do NOT use single '*text*' "
        "for emphasis at the start of lines (it renders as stray "
        "asterisks in PDF).\n"
        "- Place '\\newpage' on its own line between major sub-tables "
        "or before new subsections that should start on a fresh page.\n"
        "- Do NOT wrap section headings in bold markers. "
        "'# 9. Title' is correct, '# **9. Title**' is wrong.\n"
        "- Use field labels with bold formatting for structured data "
        "(e.g., '**Study Title:** ...'). Do not use bullet lists "
        "for metadata fields on the title page."
    )

    return instruction


def _build_section_1_instruction(guidelines):
    """Build a highly specific instruction for Section 1 (Title Page).

    Uses the structured required_fields_in_order from the guidelines to
    produce an exact field-by-field specification with search queries.
    """
    section_data = guidelines.get("Sections", {}).get("Section_1", {})
    date_rule = section_data.get("date_format_rule", "")
    dna_handling = section_data.get("data_not_available_handling", "")
    gcp_stmt = section_data.get("gcp_statement", {})
    gcp_template = gcp_stmt.get("template", "")

    # Build the field specification from required_fields_in_order
    fields = section_data.get("required_fields_in_order", [])
    field_spec_lines = []
    search_queries = []
    for i, field in enumerate(fields, 1):
        label = field.get("label", "")
        desc = field.get("description", "")
        example = field.get("example", "")
        query = field.get("search_query", "")
        field_spec_lines.append(
            f"  {i}. **{label}**\n"
            f"     Description: {desc}\n"
            f"     Example: {example}"
        )
        if query:
            search_queries.append(f"  - '{query}'")

    field_spec = "\n".join(field_spec_lines)
    queries_text = "\n".join(search_queries)

    global_rules = guidelines.get("Global_Writing_Constraints", [])
    forbidden = guidelines.get("Forbidden_Actions", [])
    safety_checks = section_data.get("critical_safety_checks", [])

    instruction = (
        "You are a regulatory medical writer generating the Title Page "
        "(Section 1) of a Clinical Study Report (CSR).\n\n"
        "GLOBAL CONSTRAINTS:\n"
        + "\n".join(f"  - {r}" for r in global_rules[:10])
        + "\n\nFORBIDDEN:\n"
        + "\n".join(f"  - {f}" for f in forbidden[:10])
        + f"\n\nDATE FORMAT RULE:\n  {date_rule}\n\n"
        f"MISSING DATA:\n  {dna_handling}\n\n"
        "═══════════════════════════════════════════════════\n"
        "EXACT OUTPUT FORMAT\n"
        "═══════════════════════════════════════════════════\n\n"
        "Your output must follow this EXACT structure:\n\n"
        "```\n"
        "# 1. Title Page\n\n"
        "**Vaccine Name and Compound Number:** <value>\n\n"
        "**Report Title:** <value>\n\n"
        "**Protocol Number:** <value>\n\n"
        "**Sponsor:** <value>\n\n"
        "**Sponsor Agent:** <value>\n\n"
        "**Phase of Development:** <value>\n\n"
        "**First Subject First Visit:** <date> (<label>); <date> (<label>)\n\n"
        "**Primary Completion Date:** <date or 'Not applicable'>\n\n"
        "**Data Cutoff Date:** <date>\n\n"
        "**Name and Affiliation of Coordinating/Leading Investigator:**\n"
        "<Full Name, Degrees>\n"
        "<Institution Name>\n"
        "<Street Address>\n"
        "<City, State ZIP>\n\n"
        "The names of the principal investigators...(appendix reference)\n\n"
        "**Sponsor's Signatories:**\n"
        "<Name, Degrees>\n"
        "<Title, Organization>\n\n"
        "<Name, Degrees>\n"
        "<Title, Organization>\n\n"
        "**Internal Reports Referenced:**\n"
        "<Protocol Report Type>:\n"
        "dated <DD Month YYYY>\n\n"
        "**Date of Current Version:** <DD Month YYYY>\n\n"
        "**Date(s) of Previous Report(s):** <DD Month YYYY>\n\n"
        "## GCP STATEMENT\n\n"
        "<GCP compliance paragraph>\n"
        "```\n\n"
        "═══════════════════════════════════════════════════\n"
        "FIELD SPECIFICATIONS (in order)\n"
        "═══════════════════════════════════════════════════\n\n"
        + field_spec
        + "\n\n"
        "═══════════════════════════════════════════════════\n"
        "SEARCH STRATEGY\n"
        "═══════════════════════════════════════════════════\n\n"
        "Call reasoning_search with these queries (one call per query):\n"
        + queries_text
        + "\n\n"
        "Do NOT call list_tables or get_table — no tables on title page.\n\n"
        "IMPORTANT RULES:\n"
        "- Use ONLY data found via reasoning_search. Never invent.\n"
        "- Every date must be DD Month YYYY with zero-padded day.\n"
        "- Convert any date format found in source docs to DD Month YYYY.\n"
        "- If data not found after searching, use '[Data Not Available]'.\n"
        "- Omit fields marked conditional (Sponsor Agent, Early Termination,\n"
        "  Internal Reports, Previous Reports) ONLY if truly not applicable.\n"
        "- Do NOT include any planning text, reasoning, or tool commentary.\n"
        "- Output ONLY the final polished markdown.\n\n"
        "GCP STATEMENT TEXT (use exactly):\n"
        f"  {gcp_template}\n\n"
        "CRITICAL CHECKS:\n"
        + "\n".join(f"  - {c}" for c in safety_checks)
    )
    return instruction


def _build_section_8_instruction(guidelines):
    base = _build_section_instruction(guidelines, "Section_8")
    extra = (
        "\n\nSPECIAL INSTRUCTIONS FOR STUDY OBJECTIVES:\n"
        "1. Generate the narrative text for study objectives first.\n"
        "2. Then call the get_table tool to fetch the following tables:\n"
        '   - "Phase 1 Objectives"\n'
        '   - "Phase 2/3 Primary Objectives"\n'
        '   - "Phase 2/3 Secondary Objectives"\n'
        "3. Format each table with a title line and a table number "
        '(e.g., "Table 8.1: Phase 1 Study Objectives").\n'
        "4. If a table is not found, generate the table structure from "
        "the study data using reasoning_search.\n"
        "5. Ensure each table has proper column headers and alignment."
    )
    return base + extra


def _build_section_11_instruction(guidelines):
    base = _build_section_instruction(guidelines, "Section_11")
    extra = (
        "\n\nSPECIAL INSTRUCTIONS FOR EFFICACY EVALUATION:\n"
        "- In Section 11.3 (Patient Flow and Relationship Between "
        "Analysis Groups), do NOT generate ASCII art diagrams, text-based "
        "flow charts, or code block diagrams. These render poorly in the "
        "final PDF and appear cropped. Instead, describe the patient flow "
        "narratively and reference the efficacy populations table for "
        "detailed numbers and exclusion reasons.\n"
        "- Present all patient flow data in tabular or narrative form only."
    )
    return base + extra


def _build_section_12_instruction(guidelines):
    base = _build_section_instruction(guidelines, "Section_12")
    extra = (
        "\n\nSPECIAL INSTRUCTIONS FOR SAFETY EVALUATION:\n"
        "- Do NOT include subsection 12.2.4 (Deaths, Other Serious "
        "Adverse Events, and Other Significant Adverse Events) or any "
        "of its sub-sections (12.2.4.1 Listing of Deaths, 12.2.4.2 "
        "Listing of Other Serious Adverse Events, 12.2.4.3 Listing of "
        "Other Significant Adverse Events). These detailed listings are "
        "provided in Section 14 and should not be duplicated in the "
        "body text.\n"
        "- After Section 12.2.3, proceed directly to Section 12.2.5 "
        "(Assessment of Significance).\n"
        "- The deaths table (Listing of Deaths) must NOT appear in "
        "Section 12. It belongs exclusively in Section 14."
    )
    return base + extra


def create_csr_agents():
    guidelines = _load_guidelines()
    agents = {}

    for section_key, section_name in SECTION_MAP.items():
        if section_key == "Section_1":
            instruction = _build_section_1_instruction(guidelines)
        elif section_key == "Section_8":
            instruction = _build_section_8_instruction(guidelines)
        elif section_key == "Section_11":
            instruction = _build_section_11_instruction(guidelines)
        elif section_key == "Section_12":
            instruction = _build_section_12_instruction(guidelines)
        else:
            instruction = _build_section_instruction(
                guidelines, section_key
            )

        agent = Agent(
            name=f"{section_key}_Writer",
            model=AGENT_MODEL,
            instruction=instruction,
            tools=[reasoning_search, get_table, list_tables],
            generate_content_config=types.GenerateContentConfig(
                temperature=0.2,
            ),
        )
        agents[section_key] = agent
        logger.info("Created agent for %s: %s.", section_key, section_name)

    qa_agent = Agent(
        name="Internal_QA_Agent",
        model=AGENT_MODEL,
        instruction=(
            "You are a compliance review agent. Your only task is to "
            "review a given Markdown text. Check for the following "
            "violations:\n"
            "1. Presence of any local file paths or source document "
            "names (e.g., 'TLF2.pdf', '/home/', 'ocr-output/').\n"
            "2. Incomplete tables or content.\n"
            "3. Stray characters like '*' after tables.\n"
            "4. Any content that seems like a placeholder (e.g., "
            "'[INSERT HERE]', 'TODO', 'TBD', '[XX.X]', '[Number]', "
            "'[YY.Y]').\n"
            "5. Missing table numbers or titles.\n"
            "6. Internal reasoning or meta-commentary text (e.g., "
            "'The reasoning_search returned...', 'I will now...', "
            "'Let me try...', 'Based on the tool output...'). The "
            "section must read as a polished regulatory document.\n"
            "7. Non-standard section numbering (e.g., '4.1 1.1' "
            "instead of just '1.1').\n"
            "8. Wrong heading levels: the main section heading must "
            "use single '#' (e.g., '# 9. Investigational Plan'), "
            "not '##' or '###'. Subsections use '##', sub-subsections "
            "use '###'.\n"
            "9. Asterisk bullet lists: lines starting with '* ' must "
            "use '- ' instead, as asterisks cause PDF rendering issues.\n"
            "10. Bold-wrapped headings: '# **9. Title**' is wrong, "
            "should be '# 9. Title' (no bold markers in headings).\n"
            "If any violation is found, respond with a JSON object: "
            "{'pass': false, 'reason': 'Describe the violation and "
            "line number.'}. If it passes, respond with {'pass': true}."
        ),
        tools=[],
    )
    agents["QA"] = qa_agent
    logger.info("Created Internal QA Agent.")

    return agents
