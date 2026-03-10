import os
import random
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import models
import schemas

router = APIRouter(prefix="/api/documents", tags=["Documents"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Simulated extraction templates per document type
EXTRACTION_TEMPLATES = {
    "tax_return": {
        "gross_income": lambda r: round(r * random.uniform(0.92, 1.08), 2),
        "net_income": lambda r: round(r * random.uniform(0.55, 0.75), 2),
        "total_deductions": lambda r: round(r * random.uniform(0.20, 0.35), 2),
        "tax_year": "2024",
        "filing_status": random.choice(["Single", "Married Filing Jointly", "S-Corporation"]),
    },
    "bank_statement": {
        "total_deposits_12mo": lambda r: round(r * random.uniform(0.90, 1.10), 2),
        "total_withdrawals_12mo": lambda r: round(r * random.uniform(0.60, 0.80), 2),
        "avg_daily_balance": lambda r: round((r / 12) * random.uniform(0.04, 0.18), 2),
        "statement_period": "Jan 2024 - Dec 2024",
        "account_type": "Business Checking",
    },
    "id": {
        "document_type": "Driver License",
        "state_issued": "CA",
        "expiry_date": "2028-06-15",
        "dob": "1985-03-22",
    },
    "business_license": {
        "license_number": f"BL-{random.randint(100000, 999999)}",
        "issue_date": "2022-01-01",
        "expiry_date": "2025-12-31",
        "business_type": "LLC",
        "registered_agent": "N/A",
    },
}


def simulate_extraction(doc_type: str, annual_revenue: float = 200_000) -> dict:
    template = EXTRACTION_TEMPLATES.get(doc_type, {})
    result = {}
    for key, val in template.items():
        if callable(val):
            result[key] = val(annual_revenue)
        else:
            result[key] = val
    return result


def simulate_tamper_score(filename: str) -> float:
    """
    Simulate document tamper detection.
    In production this would call a vision model / metadata analyzer.
    Returns a score 0-100 (>15 = flagged).
    """
    # Introduce occasional fraud for demo realism
    roll = random.random()
    if roll < 0.05:    # 5% chance of high tamper
        return round(random.uniform(20, 85), 2)
    elif roll < 0.12:  # 7% chance of borderline
        return round(random.uniform(10, 20), 2)
    else:
        return round(random.uniform(0, 8), 2)


@router.post("/upload", response_model=schemas.DocumentResponse, status_code=201)
async def upload_document(
    application_id: int = Form(...),
    doc_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    app = db.query(models.Application).filter(models.Application.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    # Save file
    ext = os.path.splitext(file.filename or "doc.pdf")[1]
    safe_name = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(UPLOAD_DIR, safe_name)
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    # Simulate processing
    tamper_score = simulate_tamper_score(file.filename or "")
    extracted = simulate_extraction(doc_type, app.annual_revenue or 200_000)
    doc_status = "flagged" if tamper_score > 15 else "processed"

    doc = models.Document(
        application_id=application_id,
        doc_type=doc_type,
        filename=file.filename or safe_name,
        file_size=len(content),
        tamper_score=tamper_score,
        extracted_data=extracted,
        status=doc_status,
    )
    db.add(doc)

    # Log event
    log = models.AuditLog(
        application_id=application_id,
        event_type="DOCUMENT_UPLOADED",
        details={
            "doc_type": doc_type,
            "filename": file.filename,
            "tamper_score": tamper_score,
            "status": doc_status,
        },
    )
    db.add(log)
    db.commit()
    db.refresh(doc)
    return doc


@router.get("/{application_id}", response_model=List[schemas.DocumentResponse])
def list_documents(application_id: int, db: Session = Depends(get_db)):
    return (
        db.query(models.Document)
        .filter(models.Document.application_id == application_id)
        .order_by(models.Document.uploaded_at.desc())
        .all()
    )


@router.delete("/{doc_id}", status_code=204)
def delete_document(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(doc)
    db.commit()
