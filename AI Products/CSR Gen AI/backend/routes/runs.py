"""Run routes: CRUD, file upload, download, retry, rerun."""

import asyncio
import os
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..config import UPLOAD_DIR, OUTPUT_DIR, SECTION_MAP, GENERATED_SECTIONS
from ..database import get_db
from ..deps import get_current_user
from ..models import Run, Section, RunDocument, AgentLog, OutputFile, User
from ..schemas import RunListItem, RunDetailOut, RerunRequest, AgentLogOut
from ..pipeline import run_pipeline, run_single_section

router = APIRouter(prefix="/runs", tags=["runs"])


def _run_to_list_item(run: Run) -> dict:
    return {
        "id": run.id,
        "run_id": run.run_id,
        "run_name": run.run_name,
        "study_id": run.study_id,
        "status": run.status,
        "started_at": run.started_at,
        "completed_at": run.completed_at,
        "created_at": run.created_at,
        "duration_minutes": run.duration_minutes,
        "initiated_by_username": run.initiated_by_user.username if run.initiated_by_user else "",
        "total_cost_usd": run.total_cost_usd,
        "total_tokens": run.total_tokens_used,
        "completed_sections": run.completed_sections,
        "failed_sections": run.failed_sections,
        "total_sections": run.total_sections,
        "total_tokens_used": run.total_tokens_used,
    }


def _run_to_detail(run: Run) -> dict:
    return {
        "id": run.id,
        "run_id": run.run_id,
        "study_id": run.study_id,
        "run_name": run.run_name,
        "status": run.status,
        "current_phase": run.current_phase,
        "started_at": run.started_at,
        "completed_at": run.completed_at,
        "created_at": run.created_at,
        "initiated_by": run.initiated_by,
        "total_input_tokens": run.total_input_tokens,
        "total_output_tokens": run.total_output_tokens,
        "total_cost_usd": run.total_cost_usd,
        "error_message": run.error_message,
        "parent_run_id": run.parent_run_id,
        "completed_sections": run.completed_sections,
        "failed_sections": run.failed_sections,
        "total_sections": run.total_sections,
        "total_tokens_used": run.total_tokens_used,
    }


@router.get("", response_model=list[RunListItem])
def list_runs(
    limit: int = 50,
    offset: int = 0,
    status: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = db.query(Run).order_by(Run.created_at.desc())
    if status:
        q = q.filter(Run.status == status)
    runs = q.offset(offset).limit(limit).all()
    return [_run_to_list_item(r) for r in runs]


@router.get("/{run_id}", response_model=RunDetailOut)
def get_run(
    run_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return _run_to_detail(run)


@router.post("", response_model=RunDetailOut)
async def create_run(
    background_tasks: BackgroundTasks,
    run_name: str = Form(""),
    study_id: str = Form(""),
    zone_a: list[UploadFile] = File(default=[]),
    zone_b: list[UploadFile] = File(default=[]),
    zone_c: list[UploadFile] = File(default=[]),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    rid = uuid.uuid4().hex[:8].upper()

    run = Run(
        run_id=rid,
        run_name=run_name or f"Run {rid}",
        study_id=study_id,
        status="pending",
        initiated_by=user.id,
    )
    db.add(run)
    db.flush()

    # Create section rows
    for sec_num in GENERATED_SECTIONS:
        sec = Section(
            run_id=rid,
            section_number=sec_num,
            section_name=SECTION_MAP.get(sec_num, f"Section {sec_num}"),
            agent_name=f"Section_{sec_num}_Writer",
            status="pending",
        )
        db.add(sec)

    # Save uploaded files
    run_upload_dir = UPLOAD_DIR / rid
    run_upload_dir.mkdir(parents=True, exist_ok=True)

    for zone_label, files in [("A", zone_a), ("B", zone_b), ("C", zone_c)]:
        for f in files:
            if not f.filename:
                continue
            dest = run_upload_dir / zone_label / f.filename
            dest.parent.mkdir(parents=True, exist_ok=True)
            content = await f.read()
            with open(dest, "wb") as fp:
                fp.write(content)

            doc = RunDocument(
                run_id=rid,
                zone=zone_label,
                original_filename=f.filename,
                stored_path=str(dest),
                file_size_bytes=len(content),
            )
            db.add(doc)

    db.commit()
    db.refresh(run)

    # Copy uploaded source docs to the expected Study-docs-module locations
    _copy_uploads_to_study_dirs(run_upload_dir)

    # Launch pipeline in background
    background_tasks.add_task(_run_pipeline_wrapper, rid, user.id)

    return _run_to_detail(run)


def _run_pipeline_wrapper(run_id: str, user_id: int):
    """Wrapper to run the async pipeline from a sync background task."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(run_pipeline(run_id, user_id))
    finally:
        loop.close()


def _copy_uploads_to_study_dirs(run_upload_dir: Path):
    """Copy uploaded files to the directories the ingestion engine expects."""
    from ..config import BASE_DIR

    study_dir = BASE_DIR / "Study-docs-module" / "study-documents"
    study_dir.mkdir(parents=True, exist_ok=True)

    # Zone A -> study-documents (source PDFs)
    zone_a_dir = run_upload_dir / "A"
    if zone_a_dir.exists():
        for f in zone_a_dir.iterdir():
            if f.is_file():
                dest = study_dir / f.name
                if not dest.exists():
                    import shutil
                    shutil.copy2(f, dest)

    # Zone B -> study-documents (TLF files)
    zone_b_dir = run_upload_dir / "B"
    if zone_b_dir.exists():
        for f in zone_b_dir.iterdir():
            if f.is_file():
                dest = study_dir / f.name
                if not dest.exists():
                    import shutil
                    shutil.copy2(f, dest)

    # Zone C -> Guidelines-module (guideline PDFs)
    guidelines_dir = BASE_DIR / "Guidelines-module"
    guidelines_dir.mkdir(parents=True, exist_ok=True)
    zone_c_dir = run_upload_dir / "C"
    if zone_c_dir.exists():
        for f in zone_c_dir.iterdir():
            if f.is_file():
                dest = guidelines_dir / f.name
                if not dest.exists():
                    import shutil
                    shutil.copy2(f, dest)


@router.post("/{run_id}/retry/{section_number}")
async def retry_section(
    run_id: int,
    section_number: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    background_tasks.add_task(
        lambda: asyncio.run(run_single_section(run.run_id, section_number))
    )
    return {"message": f"Retrying section {section_number}"}


@router.post("/{run_id}/rerun")
async def rerun_pipeline(
    run_id: int,
    body: RerunRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    if body.scope == "section" and body.section_number:
        background_tasks.add_task(
            lambda: asyncio.run(run_single_section(run.run_id, body.section_number))
        )
        return {"message": f"Rerunning section {body.section_number}"}

    # Full rerun
    run.status = "pending"
    run.error_message = None
    for sec in run.sections:
        sec.status = "pending"
        sec.content = None
    db.commit()
    background_tasks.add_task(_run_pipeline_wrapper, run.run_id, user.id)
    return {"message": "Full pipeline rerun started"}


@router.get("/{run_id}/logs", response_model=list[AgentLogOut])
def get_logs(
    run_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    logs = (
        db.query(AgentLog)
        .filter(AgentLog.run_id == run.run_id)
        .order_by(AgentLog.timestamp)
        .all()
    )
    return [AgentLogOut.model_validate(l) for l in logs]


@router.get("/{run_id}/download/{file_type}")
def download_file(
    run_id: int,
    file_type: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    if file_type == "pdf":
        pdf_path = OUTPUT_DIR / "CSR.pdf"
        if pdf_path.exists():
            return FileResponse(
                path=str(pdf_path),
                filename=f"CSR_{run.run_id}.pdf",
                media_type="application/pdf",
            )
    elif file_type == "index_csv":
        # Return table index as CSV
        import json
        import csv
        import io
        from fastapi.responses import StreamingResponse

        index_path = OUTPUT_DIR / "table_index.json"
        if index_path.exists():
            with open(index_path) as f:
                tables = json.load(f)
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=["num", "title", "label"])
            writer.writeheader()
            for t in tables:
                writer.writerow(t)
            output.seek(0)
            return StreamingResponse(
                iter([output.getvalue()]),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=table_index_{run.run_id}.csv"},
            )

    raise HTTPException(status_code=404, detail=f"File type '{file_type}' not available")
