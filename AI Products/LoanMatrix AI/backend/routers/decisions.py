from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database import get_db
import models
import schemas
from services.scoring import generate_offers

router = APIRouter(prefix="/api/decisions", tags=["Decisions"])


@router.get("/{app_id}", response_model=schemas.DecisionResponse)
def get_decision(app_id: int, db: Session = Depends(get_db)):
    decision = db.query(models.Decision).filter(models.Decision.application_id == app_id).first()
    if not decision:
        raise HTTPException(status_code=404, detail="No decision found for this application")
    return decision


@router.post("/{app_id}/manual", response_model=schemas.DecisionResponse)
def manual_decision(app_id: int, payload: schemas.ManualDecisionCreate, db: Session = Depends(get_db)):
    app = db.query(models.Application).filter(models.Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    # Update existing decision or create new
    decision = db.query(models.Decision).filter(models.Decision.application_id == app_id).first()
    if not decision:
        decision = models.Decision(application_id=app_id, shap_values={})
        db.add(decision)

    decision.decision_type = payload.decision_type
    decision.notes = payload.notes
    decision.decided_by = payload.decided_by
    decision.decided_at = datetime.utcnow()

    if payload.decision_type == "manual_approve":
        decision.final_rate = payload.final_rate
        decision.final_amount = payload.final_amount
        decision.final_term_months = payload.final_term_months
        app.status = "auto_approved"

        # Create a custom offer
        if payload.final_amount and payload.final_rate and payload.final_term_months:
            rate_mo = payload.final_rate / 100 / 12
            n = payload.final_term_months
            monthly = payload.final_amount * (rate_mo * (1 + rate_mo) ** n) / ((1 + rate_mo) ** n - 1)
            offer = models.Offer(
                application_id=app_id,
                product_type="term_loan",
                rate=payload.final_rate,
                term_months=payload.final_term_months,
                amount=payload.final_amount,
                monthly_payment=round(monthly, 2),
            )
            db.add(offer)

    elif payload.decision_type == "manual_decline":
        app.status = "auto_declined"
        decision.reasons = payload.decline_reasons or ["Underwriter judgment"]
        decision.adverse_action_codes = payload.decline_reasons

    elif payload.decision_type == "request_more_info":
        app.status = "referred"

    # Audit log
    log = models.AuditLog(
        application_id=app_id,
        event_type="MANUAL_DECISION",
        details={
            "decision_type": payload.decision_type,
            "decided_by": payload.decided_by,
            "notes": payload.notes,
        },
    )
    db.add(log)
    db.commit()
    db.refresh(decision)
    return decision


@router.get("/{app_id}/adverse-action")
def generate_adverse_action(app_id: int, db: Session = Depends(get_db)):
    app = db.query(models.Application).filter(models.Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    decision = db.query(models.Decision).filter(models.Decision.application_id == app_id).first()
    if not decision:
        raise HTTPException(status_code=404, detail="No decision found")

    return {
        "applicant_name": app.applicant_name,
        "applicant_email": app.applicant_email,
        "application_id": app_id,
        "decision_date": decision.decided_at.strftime("%B %d, %Y") if decision.decided_at else "N/A",
        "loan_amount_requested": app.loan_amount,
        "adverse_action_codes": decision.adverse_action_codes or [],
        "reasons": decision.reasons or [],
        "notice_text": f"""
ADVERSE ACTION NOTICE
Pursuant to the Equal Credit Opportunity Act (ECOA) and Fair Credit Reporting Act (FCRA)

Date: {decision.decided_at.strftime("%B %d, %Y") if decision.decided_at else "N/A"}

Dear {app.applicant_name or "Applicant"},

We regret to inform you that your application for a business loan in the amount of
${app.loan_amount:,.0f} has been DECLINED.

PRINCIPAL REASONS FOR ADVERSE ACTION:
{chr(10).join(f"  {i+1}. {r}" for i, r in enumerate(decision.adverse_action_codes or decision.reasons or ["See reasons above"]))}

You have the right to:
- Request the specific reasons for this decision within 60 days of this notice.
- Obtain a free copy of your credit report if a credit report was used in this decision.
- Dispute inaccurate information in your credit report.

For questions, contact: compliance@loanmatrix.ai | 1-800-LOAN-MTX

LoanMatrix AI | NMLS #000000 | Equal Opportunity Lender
        """.strip(),
    }
