import asyncio
import json
import logging
import re
import sys
from pathlib import Path

from google.adk.runners import InMemoryRunner
from google.genai import types

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "Study-docs-module"))
from ingestion_engine import StudyIngestionEngine

from agents import create_csr_agents, SECTION_MAP
from publisher import main as publish_pdf

logger = logging.getLogger(__name__)

OUTPUT_DIR = Path(__file__).resolve().parent / "output"
MAX_QA_RETRIES = 2


def _postprocess_section(content, section_key):
    """Apply formatting fixes to generated section content.

    Fixes common LLM output issues:
    - Asterisk bullets ('* ') -> dash bullets ('- ')
    - Wrong heading levels (## for main heading -> #)
    - Bold-wrapped headings ('# **X. Title**' -> '# X. Title')
    - Stray asterisk lines
    - Section 11: Remove ASCII/text-based flow diagrams
    - Section 12: Remove subsection 12.2.4 (Deaths listings)
    """
    section_num = section_key.replace("Section_", "")
    lines = content.split("\n")
    fixed_lines = []

    for line in lines:
        # Fix asterisk bullets: '* text' or '*   text' -> '- text'
        line = re.sub(r"^\*\s{1,4}(\S)", r"- \1", line)

        # Fix bold-wrapped headings: '# **X. Title**' -> '# X. Title'
        line = re.sub(
            r"^(#{1,4})\s+\*\*(.+?)\*\*\s*$",
            r"\1 \2",
            line,
        )

        # Remove lines that are just a stray asterisk
        if line.strip() == "*":
            continue

        fixed_lines.append(line)

    content = "\n".join(fixed_lines)

    # Fix main heading level: if the first heading uses ## instead of #,
    # adjust all heading levels down by one
    main_heading_pattern = re.compile(
        rf"^##\s+{re.escape(section_num)}\.", re.MULTILINE
    )
    if main_heading_pattern.search(content):
        logger.info(
            "Fixing heading levels for %s (## -> #).", section_key
        )
        # Adjust from deepest to shallowest to avoid double-replacement
        content = re.sub(r"^####\s+", "### ", content, flags=re.MULTILINE)
        content = re.sub(r"^###\s+", "## ", content, flags=re.MULTILINE)
        content = re.sub(r"^##\s+", "# ", content, flags=re.MULTILINE)

    # Section 11: Remove ASCII/text-based flow diagrams (code blocks with
    # arrows or bracketed population labels) that render poorly in PDF
    if section_key == "Section_11":
        content = re.sub(
            r"```[^\n]*\n(?:.*?(?:\[.*?Population.*?\]|↓|→).*?\n)*?```",
            "The patient flow data, including the number of subjects in "
            "each analysis population and the reasons for exclusion at "
            "each stage, are detailed in Table 1 above.",
            content,
            flags=re.DOTALL,
        )
        logger.info("Removed text-based flow diagrams from Section 11.")

    # Section 12: Remove subsection 12.2.4 (Deaths, Other Serious AEs,
    # Other Significant AEs) - these listings belong in Section 14 only
    if section_key == "Section_12":
        content = re.sub(
            r"#{2,4}\s*12\.2\.4\s+Deaths.*?"
            r"(?=#{2,3}\s*12\.2\.5|#{2}\s*12\.3|$)",
            "",
            content,
            flags=re.DOTALL,
        )
        # Clean up any resulting double newpages
        content = re.sub(
            r"(\\newpage\s*\n\s*){2,}",
            "\\newpage\n\n",
            content,
        )
        logger.info("Removed section 12.2.4 from Section 12.")

    return content


async def _run_agent(runner, section_key, prompt):
    session_id = f"session_{section_key}"
    user_id = "csr_orchestrator"

    await runner.session_service.create_session(
        app_name=runner.app_name,
        user_id=user_id,
        session_id=session_id,
    )

    content = types.Content(
        role="user",
        parts=[types.Part(text=prompt)],
    )

    final_text = ""
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=content,
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    final_text += part.text

    return final_text


async def _generate_section(writer_runner, qa_runner, section_key):
    section_title = SECTION_MAP.get(section_key, section_key)
    prompt = (
        f"Generate the complete content for CSR {section_title} "
        f"({section_key}). Use the reasoning_search tool to find "
        "relevant study data and the get_table tool to retrieve "
        "any required tables. Follow all guidelines strictly."
    )

    logger.info("Generating %s: %s.", section_key, section_title)
    content = await _run_agent(writer_runner, section_key, prompt)

    for attempt in range(MAX_QA_RETRIES):
        logger.info(
            "QA review for %s (attempt %d).", section_key, attempt + 1
        )
        qa_prompt = (
            f"Review the following CSR section for compliance "
            f"violations:\n\n{content}"
        )
        qa_result = await _run_agent(
            qa_runner, f"QA_{section_key}", qa_prompt
        )

        try:
            qa_json = json.loads(qa_result)
        except json.JSONDecodeError:
            if "pass" in qa_result.lower() and "true" in qa_result.lower():
                logger.info("%s passed QA review.", section_key)
                break
            logger.warning(
                "QA returned non-JSON for %s. Treating as pass.",
                section_key,
            )
            break

        if qa_json.get("pass", False):
            logger.info("%s passed QA review.", section_key)
            break

        reason = qa_json.get("reason", "Unknown violation")
        logger.warning(
            "QA failed for %s: %s. Regenerating.", section_key, reason
        )
        regen_prompt = (
            f"Please regenerate the section {section_title}, "
            f"addressing the following issue: {reason}\n\n"
            "Use reasoning_search and get_table tools as needed. "
            "Follow all guidelines strictly."
        )
        content = await _run_agent(writer_runner, section_key, regen_prompt)
    else:
        logger.warning(
            "%s did not pass QA after %d retries. Using last version.",
            section_key,
            MAX_QA_RETRIES,
        )

    return section_key, content


async def run_csr_workflow():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger.info("Starting CSR generation workflow.")

    logger.info("Step 1: Running study document ingestion.")
    engine = StudyIngestionEngine()
    engine.run_ingestion()

    logger.info("Step 2: Initializing CSR agents.")
    agents = create_csr_agents()

    qa_agent = agents.pop("QA")
    qa_runner = InMemoryRunner(
        agent=qa_agent,
        app_name="csr_qa",
    )

    sections_to_generate = [
        key for key in SECTION_MAP if key not in ("Section_3", "Section_4")
    ]

    logger.info("Step 3: Generating %d sections.", len(sections_to_generate))

    tasks = []
    for section_key in sections_to_generate:
        writer_agent = agents[section_key]
        writer_runner = InMemoryRunner(
            agent=writer_agent,
            app_name=f"csr_{section_key}",
        )
        tasks.append(
            _generate_section(writer_runner, qa_runner, section_key)
        )

    results = await asyncio.gather(*tasks, return_exceptions=True)

    OUTPUT_DIR.mkdir(exist_ok=True)
    for result in results:
        if isinstance(result, Exception):
            logger.error("Section generation failed: %s", result)
            continue
        section_key, content = result
        content = _postprocess_section(content, section_key)
        output_path = OUTPUT_DIR / f"{section_key}.md"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info("Saved %s to %s.", section_key, output_path)

    logger.info("Step 4: Publishing final PDF.")
    try:
        publish_pdf()
        logger.info("CSR generation workflow complete.")
    except Exception:
        logger.error("PDF publishing failed.", exc_info=True)


if __name__ == "__main__":
    asyncio.run(run_csr_workflow())
