from fastapi import APIRouter, Depends
from sqlalchemy import func, case
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import models
import schemas

router = APIRouter(prefix="/api/compliance", tags=["Compliance"])


@router.get("/dashboard", response_model=schemas.ComplianceMetrics)
def compliance_dashboard(db: Session = Depends(get_db)):
    total = db.query(models.Application).count()

    status_counts = (
        db.query(models.Application.status, func.count(models.Application.id))
        .group_by(models.Application.status)
        .all()
    )
    counts = {s: c for s, c in status_counts}

    auto_approved = counts.get("auto_approved", 0)
    auto_declined = counts.get("auto_declined", 0)
    referred = counts.get("referred", 0)
    fraud_hold = counts.get("fraud_hold", 0)

    approval_rate = round((auto_approved / max(total, 1)) * 100, 1)

    scores = (
        db.query(models.Application.health_score)
        .filter(models.Application.health_score.isnot(None))
        .all()
    )
    score_list = [s[0] for s in scores if s[0] is not None]
    avg_score = round(sum(score_list) / len(score_list), 1) if score_list else 0

    # By business type
    by_type = (
        db.query(
            models.Application.business_type,
            func.count(models.Application.id),
            func.sum(case((models.Application.status == "auto_approved", 1), else_=0)),
        )
        .filter(models.Application.business_type.isnot(None))
        .group_by(models.Application.business_type)
        .all()
    )
    by_business_type = {
        bt: {"total": t, "approved": int(a or 0), "rate": round(int(a or 0) / max(t, 1) * 100, 1)}
        for bt, t, a in by_type
    }

    # By industry
    by_ind = (
        db.query(
            models.Application.industry,
            func.count(models.Application.id),
            func.sum(case((models.Application.status == "auto_approved", 1), else_=0)),
        )
        .filter(models.Application.industry.isnot(None))
        .group_by(models.Application.industry)
        .all()
    )
    by_industry = {
        ind: {"total": t, "approved": int(a or 0), "rate": round(int(a or 0) / max(t, 1) * 100, 1)}
        for ind, t, a in by_ind
    }

    # Score distribution buckets
    buckets = [
        {"range": "0-200", "min": 0, "max": 200},
        {"range": "201-400", "min": 201, "max": 400},
        {"range": "401-600", "min": 401, "max": 600},
        {"range": "601-800", "min": 601, "max": 800},
        {"range": "801-1000", "min": 801, "max": 1000},
    ]
    score_distribution = []
    for b in buckets:
        count = sum(1 for s in score_list if b["min"] <= s <= b["max"])
        score_distribution.append({"range": b["range"], "count": count})

    return schemas.ComplianceMetrics(
        total_applications=total,
        auto_approved=auto_approved,
        auto_declined=auto_declined,
        referred=referred,
        fraud_hold=fraud_hold,
        approval_rate=approval_rate,
        avg_health_score=avg_score,
        by_business_type=by_business_type,
        by_industry=by_industry,
        score_distribution=score_distribution,
    )


@router.get("/audit-log", response_model=List[schemas.AuditLogResponse])
def get_audit_log(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return (
        db.query(models.AuditLog)
        .order_by(models.AuditLog.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/thresholds", response_model=schemas.ThresholdConfigResponse)
def get_thresholds(db: Session = Depends(get_db)):
    cfg = db.query(models.ThresholdConfig).order_by(models.ThresholdConfig.id.desc()).first()
    if not cfg:
        cfg = models.ThresholdConfig()
        db.add(cfg)
        db.commit()
        db.refresh(cfg)
    return cfg


@router.put("/thresholds/request", response_model=schemas.ThresholdConfigResponse)
def request_threshold_update(payload: schemas.ThresholdUpdateRequest, db: Session = Depends(get_db)):
    cfg = db.query(models.ThresholdConfig).order_by(models.ThresholdConfig.id.desc()).first()
    if not cfg:
        cfg = models.ThresholdConfig()
        db.add(cfg)

    cfg.pending_approve_min = payload.auto_approve_min
    cfg.pending_decline_max = payload.auto_decline_max
    if payload.max_loan_amount:
        cfg.max_loan_amount = payload.max_loan_amount
    if payload.min_years_in_business:
        cfg.min_years_in_business = payload.min_years_in_business
    cfg.pending_requested_by = payload.requested_by
    cfg.pending_approved_by = None

    log = models.AuditLog(
        event_type="THRESHOLD_UPDATE_REQUESTED",
        details={"requested_by": payload.requested_by, "new_approve_min": payload.auto_approve_min, "new_decline_max": payload.auto_decline_max},
    )
    db.add(log)
    db.commit()
    db.refresh(cfg)
    return cfg


@router.post("/thresholds/approve", response_model=schemas.ThresholdConfigResponse)
def approve_threshold_update(payload: schemas.ThresholdApprovalRequest, db: Session = Depends(get_db)):
    from datetime import datetime
    cfg = db.query(models.ThresholdConfig).order_by(models.ThresholdConfig.id.desc()).first()
    if not cfg or cfg.pending_approve_min is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="No pending threshold update to approve")

    cfg.auto_approve_min = cfg.pending_approve_min
    cfg.auto_decline_max = cfg.pending_decline_max
    cfg.pending_approved_by = payload.approved_by
    cfg.updated_by = f"{cfg.pending_requested_by} → {payload.approved_by}"
    cfg.pending_approve_min = None
    cfg.pending_decline_max = None
    cfg.updated_at = datetime.utcnow()

    log = models.AuditLog(
        event_type="THRESHOLD_UPDATE_APPROVED",
        details={"approved_by": payload.approved_by},
    )
    db.add(log)
    db.commit()
    db.refresh(cfg)
    return cfg
