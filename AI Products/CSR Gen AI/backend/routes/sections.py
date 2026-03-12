"""Section routes: list, get, update, rerun."""

import asyncio
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from ..config import OUTPUT_DIR, SECTION_MAP
from ..database import get_db
from ..deps import get_current_user
from ..models import Run, Section, User
from ..schemas import SectionSummary, SectionDetailOut, SectionUpdateRequest
from ..pipeline import run_single_section

router = APIRouter(tags=["sections"])


def _section_to_summary(s: Section) -> dict:
    return {
        "id": s.id,
        "run_id": s.run_id,
        "section_number": s.section_number,
        "section_name": s.section_name,
        "title": s.section_name,
        "agent_name": s.agent_name,
        "status": s.status,
        "word_count": s.word_count,
        "is_human_edited": s.is_human_edited,
        "is_edited": s.is_human_edited,
        "retry_count": s.retry_count,
        "started_at": s.started_at,
        "completed_at": s.completed_at,
        "edited_at": s.edited_at,
    }


def _section_to_detail(s: Section) -> dict:
    d = _section_to_summary(s)
    d.update({
        "content": s.content,
        "compliance_trace": s.compliance_trace,
        "data_not_available_count": s.data_not_available_count,
        "gcp_deviation_count": s.gcp_deviation_count,
        "tokens_used": s.tokens_used,
        "generation_cost_usd": s.generation_cost_usd,
        "edit_count": 0,
    })
    return d


def _get_run(db: Session, run_id: int) -> Run:
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@router.get("/runs/{run_id}/sections", response_model=list[SectionSummary])
def list_sections(
    run_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    run = _get_run(db, run_id)
    sections = (
        db.query(Section)
        .filter(Section.run_id == run.run_id)
        .order_by(Section.section_number)
        .all()
    )
    return [_section_to_summary(s) for s in sections]


@router.get("/runs/{run_id}/sections/{section_number}", response_model=SectionDetailOut)
def get_section(
    run_id: int,
    section_number: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    run = _get_run(db, run_id)
    sec = (
        db.query(Section)
        .filter(Section.run_id == run.run_id, Section.section_number == section_number)
        .first()
    )
    if not sec:
        raise HTTPException(status_code=404, detail="Section not found")

    # If content is empty, try to load from file
    if not sec.content:
        md_path = OUTPUT_DIR / f"Section_{section_number}.md"
        if md_path.exists():
            sec.content = md_path.read_text(encoding="utf-8")
            sec.word_count = len(sec.content.split())
            db.commit()

    return _section_to_detail(sec)


@router.put("/runs/{run_id}/sections/{section_number}", response_model=SectionDetailOut)
def update_section(
    run_id: int,
    section_number: int,
    body: SectionUpdateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    run = _get_run(db, run_id)
    sec = (
        db.query(Section)
        .filter(Section.run_id == run.run_id, Section.section_number == section_number)
        .first()
    )
    if not sec:
        raise HTTPException(status_code=404, detail="Section not found")

    sec.content = body.content
    sec.word_count = len(body.content.split()) if body.content else 0
    sec.is_human_edited = True
    sec.edited_at = datetime.utcnow()
    db.commit()

    # Also save to file so publisher picks it up
    OUTPUT_DIR.mkdir(exist_ok=True)
    md_path = OUTPUT_DIR / f"Section_{section_number}.md"
    md_path.write_text(body.content, encoding="utf-8")

    return _section_to_detail(sec)


@router.post("/runs/{run_id}/sections/{section_number}/rerun")
async def rerun_section(
    run_id: int,
    section_number: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    run = _get_run(db, run_id)
    background_tasks.add_task(
        lambda: asyncio.run(run_single_section(run.run_id, section_number))
    )
    return {"message": f"Regenerating section {section_number}"}
