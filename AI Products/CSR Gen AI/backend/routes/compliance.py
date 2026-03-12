"""Compliance routes: get report, sign, audit trail."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import Run, ComplianceReport, ComplianceAudit, User
from ..schemas import ComplianceReportOut, ComplianceSignRequest, ComplianceAuditOut

router = APIRouter(tags=["compliance"])


def _get_run(db: Session, run_id: int) -> Run:
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@router.get("/runs/{run_id}/compliance", response_model=ComplianceReportOut)
def get_compliance(
    run_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    run = _get_run(db, run_id)
    report = (
        db.query(ComplianceReport)
        .filter(ComplianceReport.run_id == run.run_id)
        .order_by(ComplianceReport.created_at.desc())
        .first()
    )
    if not report:
        raise HTTPException(status_code=404, detail="No compliance report found")
    return ComplianceReportOut.model_validate(report)


@router.post("/runs/{run_id}/compliance/sign")
def sign_compliance(
    run_id: int,
    body: ComplianceSignRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    run = _get_run(db, run_id)
    report = (
        db.query(ComplianceReport)
        .filter(ComplianceReport.run_id == run.run_id)
        .order_by(ComplianceReport.created_at.desc())
        .first()
    )
    if not report:
        raise HTTPException(status_code=404, detail="No compliance report found")

    if not body.acknowledged:
        raise HTTPException(status_code=400, detail="Must acknowledge compliance")

    report.is_signed = True
    report.signed_by = user.id
    report.signed_by_username = user.username
    report.signed_at = datetime.utcnow()

    audit = ComplianceAudit(
        run_id=run.run_id,
        user_id=user.id,
        username=user.username,
        action="Signed compliance report",
    )
    db.add(audit)
    db.commit()

    return {"message": "Compliance report signed"}


@router.get("/runs/{run_id}/compliance/audit", response_model=list[ComplianceAuditOut])
def get_audit(
    run_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    run = _get_run(db, run_id)
    entries = (
        db.query(ComplianceAudit)
        .filter(ComplianceAudit.run_id == run.run_id)
        .order_by(ComplianceAudit.timestamp.desc())
        .all()
    )
    return [ComplianceAuditOut.model_validate(e) for e in entries]
