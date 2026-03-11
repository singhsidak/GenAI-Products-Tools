from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import models
import schemas

router = APIRouter(prefix="/api/offers", tags=["Offers"])


@router.get("/{app_id}", response_model=List[schemas.OfferResponse])
def get_offers(app_id: int, db: Session = Depends(get_db)):
    offers = db.query(models.Offer).filter(models.Offer.application_id == app_id).all()
    return offers


@router.post("/{app_id}/accept/{offer_id}")
def accept_offer(app_id: int, offer_id: int, db: Session = Depends(get_db)):
    offer = db.query(models.Offer).filter(
        models.Offer.id == offer_id,
        models.Offer.application_id == app_id,
    ).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    app = db.query(models.Application).filter(models.Application.id == app_id).first()
    if app:
        app.status = "funded"

    log = models.AuditLog(
        application_id=app_id,
        event_type="OFFER_ACCEPTED",
        details={"offer_id": offer_id, "product_type": offer.product_type, "amount": offer.amount},
    )
    db.add(log)
    db.commit()
    return {"message": "Offer accepted. Loan queued for disbursement.", "offer_id": offer_id}
