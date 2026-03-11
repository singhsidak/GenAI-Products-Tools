from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import models
import schemas
from services.scoring import generate_credit_memo, generate_risk_alerts

router = APIRouter(prefix="/api/underwriter", tags=["Underwriter"])


@router.get("/queue", response_model=List[schemas.ApplicationResponse])
def get_queue(db: Session = Depends(get_db)):
    """Referred applications ordered by wait time (oldest first)."""
    return (
        db.query(models.Application)
        .filter(models.Application.status == "referred")
        .order_by(models.Application.created_at.asc())
        .all()
    )


@router.get("/stats")
def underwriter_stats(db: Session = Depends(get_db)):
    total = db.query(models.Application).filter(models.Application.status == "referred").count()
    avg_score = (
        db.query(models.Application)
        .filter(models.Application.status == "referred", models.Application.health_score.isnot(None))
        .with_entities(models.Application.health_score)
        .all()
    )
    scores = [r[0] for r in avg_score if r[0] is not None]
    return {
        "queue_count": total,
        "avg_health_score": round(sum(scores) / len(scores), 1) if scores else 0,
        "sla_warning_count": min(total, 2),  # simulated
    }


@router.get("/{app_id}/credit-memo")
def get_credit_memo(app_id: int, db: Session = Depends(get_db)):
    app = db.query(models.Application).filter(models.Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    memo = generate_credit_memo(app)
    return {"memo": memo, "application_id": app_id}


@router.get("/{app_id}/risk-alerts")
def get_risk_alerts_uw(app_id: int, db: Session = Depends(get_db)):
    app = db.query(models.Application).filter(models.Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    alerts = generate_risk_alerts({
        "annual_revenue": app.annual_revenue,
        "monthly_expenses": app.monthly_expenses,
        "nsf_count": app.nsf_count,
        "loan_amount": app.loan_amount,
        "years_in_business": app.years_in_business,
        "credit_score": app.credit_score,
    })
    return {"alerts": alerts, "application_id": app_id}


@router.get("/{app_id}/full")
def get_full_profile(app_id: int, db: Session = Depends(get_db)):
    """Full underwriter view: application + docs + decision + alerts + memo."""
    app = db.query(models.Application).filter(models.Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    decision = db.query(models.Decision).filter(models.Decision.application_id == app_id).first()
    documents = db.query(models.Document).filter(models.Document.application_id == app_id).all()
    offers = db.query(models.Offer).filter(models.Offer.application_id == app_id).all()

    alerts = generate_risk_alerts({
        "annual_revenue": app.annual_revenue,
        "monthly_expenses": app.monthly_expenses,
        "nsf_count": app.nsf_count,
        "loan_amount": app.loan_amount,
        "years_in_business": app.years_in_business,
        "credit_score": app.credit_score,
    })

    memo = generate_credit_memo(app)

    return {
        "application": schemas.ApplicationResponse.model_validate(app),
        "decision": schemas.DecisionResponse.model_validate(decision) if decision else None,
        "documents": [schemas.DocumentResponse.model_validate(d) for d in documents],
        "offers": [schemas.OfferResponse.model_validate(o) for o in offers],
        "risk_alerts": alerts,
        "credit_memo": memo,
    }
