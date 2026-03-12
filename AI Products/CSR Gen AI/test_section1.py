"""
Quick test script to generate Section 1 (Title Page) only.

Usage:
    python test_section1.py

Reads study data from Study-docs-module/study_data/,
uses guidelines from Guidelines-module/guidlines.json,
and writes the output to csr-generation-module/output/Section_1.md
"""

import asyncio
import json
import logging
import os
import sys
import uuid
from pathlib import Path
from dotenv import load_dotenv

# ── Setup paths ─────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

# Add module paths
sys.path.insert(0, str(ROOT / "csr-generation-module"))

# ── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("test_section1")


async def main():
    logger.info("=" * 70)
    logger.info("SECTION 1 (Title Page) — Test Generation")
    logger.info("=" * 70)

    # ── Step 1: Create agents ───────────────────────────────────────────
    logger.info("Loading guidelines and creating agents...")
    from agents import create_csr_agents
    agents = create_csr_agents()

    writer_agent = agents["Section_1"]
    qa_agent = agents["QA"]
    logger.info("Section_1 writer agent and QA agent ready.")

    # ── Step 2: Run the writer agent ────────────────────────────────────
    from google.adk.runners import InMemoryRunner
    from google.genai import types

    writer_runner = InMemoryRunner(
        agent=writer_agent, app_name="csr_Section_1"
    )
    qa_runner = InMemoryRunner(
        agent=qa_agent, app_name="csr_qa"
    )

    session_id = f"session_Section_1_{uuid.uuid4().hex[:8]}"
    user_id = "test_user"

    await writer_runner.session_service.create_session(
        app_name=writer_runner.app_name,
        user_id=user_id,
        session_id=session_id,
    )

    prompt = (
        "Generate the complete content for CSR Title Page (Section_1). "
        "Use the reasoning_search tool to find relevant study data. "
        "Follow all guidelines strictly. "
        "Do NOT call list_tables or get_table — no tables are needed."
    )

    logger.info("Sending prompt to Section_1 writer agent...")
    logger.info("-" * 70)

    content = types.Content(
        role="user",
        parts=[types.Part(text=prompt)],
    )

    final_text = ""
    async for event in writer_runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=content,
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    final_text += part.text

    logger.info("-" * 70)
    logger.info("Writer agent finished. Output length: %d chars", len(final_text))

    # ── Step 3: QA pass ─────────────────────────────────────────────────
    logger.info("Running QA agent...")
    qa_session_id = f"session_QA_{uuid.uuid4().hex[:8]}"
    await qa_runner.session_service.create_session(
        app_name=qa_runner.app_name,
        user_id=user_id,
        session_id=qa_session_id,
    )

    qa_prompt = (
        "Review the following CSR section for compliance violations:\n\n"
        + final_text
    )
    qa_content = types.Content(
        role="user",
        parts=[types.Part(text=qa_prompt)],
    )

    qa_result = ""
    async for event in qa_runner.run_async(
        user_id=user_id,
        session_id=qa_session_id,
        new_message=qa_content,
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    qa_result += part.text

    logger.info("QA result: %s", qa_result.strip()[:300])

    # ── Step 4: Post-process ────────────────────────────────────────────
    try:
        from orchestrator import _postprocess_section
        final_text = _postprocess_section(final_text, "Section_1")
        logger.info("Post-processing applied.")
    except ImportError:
        logger.warning("orchestrator module not found — skipping post-processing.")

    # ── Step 5: Save output ─────────────────────────────────────────────
    output_dir = ROOT / "csr-generation-module" / "output"
    output_dir.mkdir(exist_ok=True)
    out_path = output_dir / "Section_1.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(final_text)

    logger.info("=" * 70)
    logger.info("Section 1 saved to: %s", out_path)
    logger.info("Word count: %d", len(final_text.split()))
    logger.info("=" * 70)

    # Print the output
    print("\n" + "=" * 70)
    print("GENERATED SECTION 1 OUTPUT:")
    print("=" * 70)
    print(final_text)
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
