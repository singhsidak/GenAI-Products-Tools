from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from database import engine, Base
import models  # noqa - ensures all models are registered before create_all

from routers import applications, documents, decisions, underwriter, compliance, offers

# Create all database tables
Base.metadata.create_all(bind=engine)

# Seed default threshold config if empty
from database import SessionLocal
from models import ThresholdConfig

def seed_defaults():
    db = SessionLocal()
    try:
        if db.query(ThresholdConfig).count() == 0:
            db.add(ThresholdConfig(
                auto_approve_min=700,
                auto_decline_max=400,
                max_loan_amount=500_000.0,
                min_years_in_business=1.0,
                updated_by="system",
            ))
            db.commit()
    finally:
        db.close()

seed_defaults()

app = FastAPI(
    title="LoanMatrix AI",
    description="AI-Native Loan Origination System for SME & Unsecured Consumer Lending",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(applications.router)
app.include_router(documents.router)
app.include_router(decisions.router)
app.include_router(underwriter.router)
app.include_router(compliance.router)
app.include_router(offers.router)

# Serve uploaded files
uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")


@app.get("/api/health")
def health():
    return {"status": "ok", "version": "1.0.0", "product": "LoanMatrix AI"}
