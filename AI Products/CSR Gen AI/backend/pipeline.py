"""Pipeline runner — bridges the frontend API to the CSR orchestrator.

Runs the CSR generation pipeline in a background asyncio task, emitting
WebSocket events and updating the database as sections complete.
"""

import asyncio
import logging
import os
import shutil
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from logging import Handler

from sqlalchemy.orm import Session

from .config import BASE_DIR, OUTPUT_DIR, SECTION_MAP, GENERATED_SECTIONS
from .database import SessionLocal
from .models import (
    Run, Section, AgentLog, ComplianceReport, OutputFile, Notification,
)
from .websocket import manager

logger = logging.getLogger(__name__)

# Add module paths so we can import from the CSR modules
CSR_MODULE = BASE_DIR / "csr-generation-module"
STUDY_MODULE = BASE_DIR / "Study-docs-module"
sys.path.insert(0, str(CSR_MODULE))
sys.path.insert(0, str(STUDY_MODULE))


def _emit(run_id: str, event_type: str, payload: dict | None = None):
    """Fire-and-forget WS broadcast helper."""
    data = {
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        "payload": payload or {},
    }
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(manager.broadcast_to_run(run_id, data))
    except RuntimeError:
        pass


def _notify_user(user_id: int, run_id: str, event_type: str, message: str):
    """Create DB notification and broadcast via WS."""
    db = SessionLocal()
    try:
        n = Notification(
            user_id=user_id,
            run_id=run_id,
            event_type=event_type,
            message=message,
        )
        db.add(n)
        db.commit()
        db.refresh(n)
        data = {
            "type": "notification",
            "id": n.id,
            "run_id": run_id,
            "event_type": event_type,
            "message": message,
            "is_read": False,
            "created_at": n.created_at.isoformat(),
        }
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(manager.broadcast_to_user(user_id, data))
        except RuntimeError:
            pass
    finally:
        db.close()


def _log_agent(db: Session, run_id: str, agent_name: str, status: str,
               message: str | None = None, phase: str | None = None,
               input_tokens: int = 0, output_tokens: int = 0, cost: float = 0.0):
    """Persist an agent log entry and emit WS event."""
    log = AgentLog(
        run_id=run_id,
        agent_name=agent_name,
        phase=phase,
        status=status,
        message=message,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        estimated_cost_usd=cost,
    )
    db.add(log)
    db.commit()
    _emit(run_id, "agent_log", {
        "agent_name": agent_name,
        "phase": phase,
        "status": status,
        "message": message,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "estimated_cost_usd": cost,
    })


class _ChunkLogHandler(Handler):
    """Captures [CHUNK LOG] messages from tools.py and saves them to DB."""

    def __init__(self, db: "Session", run_id: str, section_key: str):
        super().__init__()
        self.db = db
        self.run_id = run_id
        self.section_key = section_key

    def emit(self, record: logging.LogRecord):
        msg = record.getMessage()
        if "[CHUNK LOG]" not in msg:
            return
        try:
            _log_agent(
                self.db,
                self.run_id,
                f"{self.section_key}_ChunkRetrieval",
                "info",
                msg,
                phase=f"{self.section_key}_chunks",
            )
        except Exception:
            pass


async def run_pipeline(run_id: str, user_id: int):
    """Execute the full CSR generation pipeline for a given run."""
    db = SessionLocal()
    try:
        run = db.query(Run).filter(Run.run_id == run_id).first()
        if not run:
            logger.error("Run %s not found", run_id)
            return

        run.status = "running"
        run.started_at = datetime.utcnow()
        run.current_phase = "ingestion"
        db.commit()

        _emit(run_id, "progress", {"percent": 0, "phase_label": "Starting ingestion..."})
        _log_agent(db, run_id, "Orchestrator", "started", "Pipeline started")

        # ── Step 1: Ingestion ─────────────────────────────────────────────
        try:
            _log_agent(db, run_id, "IngestionEngine", "running", "Processing study documents...")
            from ingestion_engine import StudyIngestionEngine
            engine = StudyIngestionEngine()

            # Run ingestion in a thread to avoid blocking the event loop
            await asyncio.get_event_loop().run_in_executor(None, engine.run_ingestion)

            _log_agent(db, run_id, "IngestionEngine", "completed", "Ingestion complete")
            _emit(run_id, "progress", {"percent": 10, "phase_label": "Ingestion complete"})
        except Exception as e:
            logger.error("Ingestion failed for run %s: %s", run_id, e, exc_info=True)
            _log_agent(db, run_id, "IngestionEngine", "failed", str(e))
            run.status = "failed"
            run.error_message = f"Ingestion failed: {e}"
            run.completed_at = datetime.utcnow()
            db.commit()
            _emit(run_id, "pipeline_failed", {"error": str(e)})
            _notify_user(user_id, run_id, "pipeline_failed", f"Pipeline failed: {e}")
            return

        # ── Step 2: Section generation ────────────────────────────────────
        run.current_phase = "generation"
        db.commit()

        try:
            from agents import create_csr_agents, SECTION_MAP as AGENT_SECTION_MAP
            from google.adk.runners import InMemoryRunner
            from google.genai import types
        except ImportError as e:
            logger.error("Cannot import CSR agents: %s", e)
            run.status = "failed"
            run.error_message = f"Import error: {e}"
            run.completed_at = datetime.utcnow()
            db.commit()
            _emit(run_id, "pipeline_failed", {"error": str(e)})
            return

        agents = create_csr_agents()
        qa_agent = agents.pop("QA")
        qa_runner = InMemoryRunner(agent=qa_agent, app_name="csr_qa")

        sections_to_generate = [
            k for k in AGENT_SECTION_MAP if k not in ("Section_3", "Section_4")
        ]
        total = len(sections_to_generate)

        for idx, section_key in enumerate(sections_to_generate):
            sec_num = int(section_key.replace("Section_", ""))
            sec_name = SECTION_MAP.get(sec_num, section_key)

            # Update DB section status
            sec_row = db.query(Section).filter(
                Section.run_id == run_id, Section.section_number == sec_num
            ).first()
            if sec_row:
                sec_row.status = "running"
                sec_row.started_at = datetime.utcnow()
                db.commit()

            _log_agent(db, run_id, f"Section_{sec_num}_Writer", "running",
                       f"Generating {sec_name}...", phase=sec_name)

            pct = 10 + int((idx / total) * 80)
            _emit(run_id, "progress", {"percent": pct, "phase_label": f"Generating {sec_name}"})

            try:
                writer_agent = agents[section_key]
                writer_runner = InMemoryRunner(
                    agent=writer_agent, app_name=f"csr_{section_key}"
                )

                prompt = (
                    f"Generate the complete content for CSR {sec_name} "
                    f"({section_key}). Use the reasoning_search tool to find "
                    "relevant study data and the get_table tool to retrieve "
                    "any required tables. Follow all guidelines strictly."
                )

                # Attach chunk-log handler so [CHUNK LOG] lines are persisted
                chunk_handler = _ChunkLogHandler(db, run_id, section_key)
                chunk_handler.setLevel(logging.INFO)
                tools_logger = logging.getLogger("tools")
                tools_logger.addHandler(chunk_handler)
                try:
                    content = await _run_agent_async(writer_runner, section_key, prompt)
                finally:
                    tools_logger.removeHandler(chunk_handler)

                # QA pass
                qa_prompt = f"Review the following CSR section for compliance violations:\n\n{content}"
                qa_result = await _run_agent_async(qa_runner, f"QA_{section_key}", qa_prompt)

                # Post-process (import from orchestrator)
                from orchestrator import _postprocess_section
                content = _postprocess_section(content, section_key)

                # Save to file
                OUTPUT_DIR.mkdir(exist_ok=True)
                out_path = OUTPUT_DIR / f"{section_key}.md"
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(content)

                # Update DB
                word_count = len(content.split()) if content else 0
                if sec_row:
                    sec_row.status = "completed"
                    sec_row.content = content
                    sec_row.word_count = word_count
                    sec_row.completed_at = datetime.utcnow()
                    db.commit()

                _log_agent(db, run_id, f"Section_{sec_num}_Writer", "completed",
                           f"{sec_name} generated ({word_count} words)", phase=sec_name)
                _emit(run_id, "section_complete", {
                    "section_number": sec_num, "section_name": sec_name
                })

            except Exception as e:
                logger.error("Section %s failed: %s", section_key, e, exc_info=True)
                if sec_row:
                    sec_row.status = "failed"
                    sec_row.completed_at = datetime.utcnow()
                    db.commit()
                _log_agent(db, run_id, f"Section_{sec_num}_Writer", "failed",
                           str(e), phase=sec_name)

        # ── Step 3: PDF publishing ────────────────────────────────────────
        run.current_phase = "publishing"
        db.commit()
        _emit(run_id, "progress", {"percent": 92, "phase_label": "Publishing PDF..."})
        _log_agent(db, run_id, "Publisher", "running", "Compiling final PDF")

        try:
            from publisher import main as publish_pdf
            await asyncio.get_event_loop().run_in_executor(None, publish_pdf)

            pdf_path = OUTPUT_DIR / "CSR.pdf"
            if pdf_path.exists():
                of = OutputFile(
                    run_id=run_id,
                    file_type="pdf",
                    stored_path=str(pdf_path),
                    file_size_bytes=pdf_path.stat().st_size,
                )
                db.add(of)
                db.commit()

            _log_agent(db, run_id, "Publisher", "completed", "PDF created")
        except Exception as e:
            logger.error("PDF publishing failed: %s", e, exc_info=True)
            _log_agent(db, run_id, "Publisher", "failed", str(e))

        # ── Step 4: Create compliance report ──────────────────────────────
        run.current_phase = "compliance"
        db.commit()
        _emit(run_id, "progress", {"percent": 96, "phase_label": "Running compliance check..."})

        _create_compliance_report(db, run_id)

        # ── Done ──────────────────────────────────────────────────────────
        run.status = "completed"
        run.completed_at = datetime.utcnow()
        run.current_phase = None
        db.commit()

        _emit(run_id, "progress", {"percent": 100, "phase_label": "Complete"})
        _emit(run_id, "pipeline_completed", {})
        _notify_user(user_id, run_id, "pipeline_completed",
                     f"CSR generation complete for run {run_id}")
        _log_agent(db, run_id, "Orchestrator", "completed", "Pipeline finished")

    except Exception as e:
        logger.error("Pipeline crashed for run %s: %s", run_id, e, exc_info=True)
        run = db.query(Run).filter(Run.run_id == run_id).first()
        if run:
            run.status = "failed"
            run.error_message = str(e)
            run.completed_at = datetime.utcnow()
            db.commit()
        _emit(run_id, "pipeline_failed", {"error": str(e)})
        _notify_user(user_id, run_id, "pipeline_failed", f"Pipeline crashed: {e}")
    finally:
        db.close()


async def run_single_section(run_id: str, section_number: int):
    """Re-generate a single section."""
    db = SessionLocal()
    try:
        section_key = f"Section_{section_number}"
        sec_name = SECTION_MAP.get(section_number, section_key)

        sec_row = db.query(Section).filter(
            Section.run_id == run_id,
            Section.section_number == section_number,
        ).first()
        if sec_row:
            sec_row.status = "running"
            sec_row.retry_count += 1
            sec_row.started_at = datetime.utcnow()
            db.commit()

        from agents import create_csr_agents
        from google.adk.runners import InMemoryRunner

        agents = create_csr_agents()
        writer_agent = agents.get(section_key)
        if not writer_agent:
            raise ValueError(f"No agent for {section_key}")

        writer_runner = InMemoryRunner(agent=writer_agent, app_name=f"csr_{section_key}")
        prompt = (
            f"Generate the complete content for CSR {sec_name} "
            f"({section_key}). Use the reasoning_search tool to find "
            "relevant study data and the get_table tool to retrieve "
            "any required tables. Follow all guidelines strictly."
        )
        content = await _run_agent_async(writer_runner, section_key, prompt)

        from orchestrator import _postprocess_section
        content = _postprocess_section(content, section_key)

        OUTPUT_DIR.mkdir(exist_ok=True)
        out_path = OUTPUT_DIR / f"{section_key}.md"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)

        if sec_row:
            sec_row.status = "completed"
            sec_row.content = content
            sec_row.word_count = len(content.split()) if content else 0
            sec_row.completed_at = datetime.utcnow()
            db.commit()

        # Republish PDF
        from publisher import main as publish_pdf
        await asyncio.get_event_loop().run_in_executor(None, publish_pdf)

        _emit(run_id, "section_complete", {
            "section_number": section_number, "section_name": sec_name
        })

    except Exception as e:
        logger.error("Section rerun failed: %s", e, exc_info=True)
        if sec_row:
            sec_row.status = "failed"
            sec_row.completed_at = datetime.utcnow()
            db.commit()
    finally:
        db.close()


async def _run_agent_async(runner, section_key: str, prompt: str) -> str:
    """Run a Google ADK agent and collect the text output."""
    from google.genai import types

    session_id = f"session_{section_key}_{uuid.uuid4().hex[:8]}"
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


def _create_compliance_report(db: Session, run_id: str):
    """Create a basic compliance report from section data."""
    sections = db.query(Section).filter(Section.run_id == run_id).all()

    total_dna = sum(s.data_not_available_count for s in sections)
    total_gcp = sum(s.gcp_deviation_count for s in sections)
    failed = sum(1 for s in sections if s.status == "failed")

    overall = "pass" if failed == 0 and total_gcp == 0 else "needs_review"

    report = ComplianceReport(
        run_id=run_id,
        version_id=f"v1-{uuid.uuid4().hex[:8]}",
        overall_status=overall,
        data_not_available_count=total_dna,
        gcp_deviation_count=total_gcp,
        report_content={
            "sections_completed": len([s for s in sections if s.status == "completed"]),
            "sections_failed": failed,
            "total_sections": len(sections),
        },
    )
    db.add(report)
    db.commit()

    if overall == "needs_review":
        _emit(run_id, "compliance_review_required", {})
