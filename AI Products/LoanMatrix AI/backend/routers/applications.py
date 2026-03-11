from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import random
from datetime import datetime

from database import get_db
import models
import schemas
from services.scoring import calculate_health_score, generate_offers, generate_risk_alerts

router = APIRouter(prefix="/api/applications", tags=["Applications"])


def _log(db: Session, app_id: int, event_type: str, details: dict):
    log = models.AuditLog(application_id=app_id, event_type=event_type, details=details)
    db.add(log)


@router.post("", response_model=schemas.ApplicationResponse, status_code=201)
def create_application(payload: schemas.ApplicationCreate, db: Session = Depends(get_db)):
    app = models.Application(**payload.model_dump(exclude_none=True))
    db.add(app)
    db.commit()
    db.refresh(app)
    _log(db, app.id, "APPLICATION_CREATED", {"session_id": app.session_id})
    db.commit()
    return app


@router.get("", response_model=List[schemas.ApplicationResponse])
def list_applications(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    q = db.query(models.Application)
    if status:
        q = q.filter(models.Application.status == status)
    return q.order_by(models.Application.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{app_id}", response_model=schemas.ApplicationResponse)
def get_application(app_id: int, db: Session = Depends(get_db)):
    app = db.query(models.Application).filter(models.Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app


@router.get("/session/{session_id}", response_model=schemas.ApplicationResponse)
def get_by_session(session_id: str, db: Session = Depends(get_db)):
    app = db.query(models.Application).filter(models.Application.session_id == session_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Session not found")
    return app


@router.put("/{app_id}", response_model=schemas.ApplicationResponse)
def update_application(app_id: int, payload: schemas.ApplicationUpdate, db: Session = Depends(get_db)):
    app = db.query(models.Application).filter(models.Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(app, field, value)
    app.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(app)
    return app


@router.post("/{app_id}/bank-connect", response_model=schemas.ApplicationResponse)
def connect_bank(app_id: int, db: Session = Depends(get_db)):
    """Simulate Plaid / Open Banking connection."""
    app = db.query(models.Application).filter(models.Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    # Simulate fetched bank data
    revenue = app.annual_revenue or 120_000
    app.bank_connected = True
    app.avg_bank_balance = round(revenue * random.uniform(0.04, 0.18), 2)
    app.nsf_count = random.choices([0, 0, 0, 1, 2, 3, 5], weights=[40, 20, 15, 10, 8, 5, 2])[0]
    app.monthly_deposits_avg = round(revenue / 12 * random.uniform(0.9, 1.1), 2)
    app.updated_at = datetime.utcnow()

    _log(db, app.id, "BANK_CONNECTED", {
        "avg_bank_balance": app.avg_bank_balance,
        "nsf_count": app.nsf_count,
        "monthly_deposits_avg": app.monthly_deposits_avg,
    })
    db.commit()
    db.refresh(app)
    return app


@router.post("/{app_id}/submit", response_model=dict)
def submit_application(app_id: int, db: Session = Depends(get_db)):
    """Submit application and trigger AI decision engine."""
    app = db.query(models.Application).filter(models.Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    if app.status not in ("draft",):
        raise HTTPException(status_code=400, detail="Application already submitted")

    # Validate minimum fields
    required = ["applicant_name", "loan_amount", "annual_revenue", "credit_score", "years_in_business"]
    missing = [f for f in required if not getattr(app, f)]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing required fields: {', '.join(missing)}")

    # Get current thresholds
    threshold = db.query(models.ThresholdConfig).order_by(models.ThresholdConfig.id.desc()).first()
    if not threshold:
        threshold = models.ThresholdConfig()
        db.add(threshold)
        db.commit()

    # Score the application
    health_score, shap_values, top_negatives = calculate_health_score(
        credit_score=app.credit_score or 650,
        annual_revenue=app.annual_revenue or 0,
        years_in_business=app.years_in_business or 0,
        monthly_expenses=app.monthly_expenses or 0,
        loan_amount=app.loan_amount or 0,
        avg_bank_balance=app.avg_bank_balance,
        nsf_count=app.nsf_count or 0,
        bank_connected=app.bank_connected,
    )

    app.health_score = health_score
    app.status = "submitted"

    # Check for fraud flags in documents
    fraud_docs = db.query(models.Document).filter(
        models.Document.application_id == app_id,
        models.Document.tamper_score > 15.0,
    ).count()

    if fraud_docs > 0:
        app.status = "fraud_hold"
        decision_type = "fraud_hold"
        reasons = ["Document tampering detected. Application routed to Fraud Investigation Team."]
    elif health_score >= threshold.auto_approve_min:
        app.status = "auto_approved"
        decision_type = "auto_approve"
        reasons = ["Strong credit profile", "Adequate cash flow", "Loan-to-revenue ratio within limits"]
    elif health_score <= threshold.auto_decline_max:
        app.status = "auto_declined"
        decision_type = "auto_decline"
        reasons = [f"Health Score ({health_score}) below minimum threshold ({threshold.auto_decline_max})"]
    else:
        app.status = "referred"
        decision_type = "referred"
        reasons = ["Application requires human underwriter review", f"Health Score: {health_score} (in review band)"]

    # ECOA adverse action codes for declines
    adverse_codes = None
    if decision_type in ("auto_decline",):
        from services.scoring import ECOA_CODES
        adverse_codes = [ECOA_CODES.get(f, f) for f in top_negatives]

    # Store decision
    existing = db.query(models.Decision).filter(models.Decision.application_id == app_id).first()
    if existing:
        db.delete(existing)
        db.flush()

    decision = models.Decision(
        application_id=app_id,
        decision_type=decision_type,
        reasons=reasons,
        shap_values=shap_values,
        adverse_action_codes=adverse_codes,
        decided_by="ai",
    )
    db.add(decision)

    # Generate offers for approved applications
    if decision_type == "auto_approve":
        offers_data = generate_offers(health_score, app.loan_amount or 0, app.annual_revenue or 0)
        for o in offers_data:
            offer = models.Offer(application_id=app_id, **o)
            db.add(offer)

    _log(db, app_id, "AI_DECISION", {
        "health_score": health_score,
        "decision": decision_type,
        "shap_values": shap_values,
    })
    db.commit()
    db.refresh(app)

    return {
        "application_id": app_id,
        "health_score": health_score,
        "decision": decision_type,
        "status": app.status,
    }


@router.get("/{app_id}/risk-alerts", response_model=List[dict])
def get_risk_alerts(app_id: int, db: Session = Depends(get_db)):
    app = db.query(models.Application).filter(models.Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return generate_risk_alerts({
        "annual_revenue": app.annual_revenue,
        "monthly_expenses": app.monthly_expenses,
        "nsf_count": app.nsf_count,
        "loan_amount": app.loan_amount,
        "years_in_business": app.years_in_business,
        "credit_score": app.credit_score,
    })
