from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
from database import Base


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, default=lambda: str(uuid.uuid4()), unique=True, index=True)

    # Personal / Business Info
    applicant_name = Column(String, nullable=True)
    applicant_email = Column(String, nullable=True)
    applicant_phone = Column(String, nullable=True)
    business_name = Column(String, nullable=True)
    business_type = Column(String, nullable=True)   # sole_proprietor | llc | corporation
    ein = Column(String, nullable=True)
    years_in_business = Column(Float, nullable=True)
    industry = Column(String, nullable=True)
    state = Column(String, nullable=True)

    # Financials
    annual_revenue = Column(Float, nullable=True)
    monthly_expenses = Column(Float, nullable=True)
    credit_score = Column(Integer, nullable=True)
    existing_debt = Column(Float, default=0.0)

    # Loan Request
    loan_amount = Column(Float, nullable=True)
    loan_purpose = Column(String, nullable=True)

    # Bank Data (from mock Plaid)
    bank_connected = Column(Boolean, default=False)
    avg_bank_balance = Column(Float, nullable=True)
    nsf_count = Column(Integer, default=0)
    monthly_deposits_avg = Column(Float, nullable=True)

    # Scoring & Status
    health_score = Column(Integer, nullable=True)
    status = Column(String, default="draft")
    # draft | submitted | auto_approved | auto_declined | referred | fraud_hold | funded

    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    # Relationships
    documents = relationship("Document", back_populates="application", cascade="all, delete-orphan")
    decision = relationship("Decision", back_populates="application", uselist=False, cascade="all, delete-orphan")
    offers = relationship("Offer", back_populates="application", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="application", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    doc_type = Column(String)   # id | tax_return | bank_statement | business_license
    filename = Column(String)
    file_size = Column(Integer, default=0)
    tamper_score = Column(Float, default=0.0)   # 0-100
    extracted_data = Column(JSON, nullable=True)
    status = Column(String, default="processing")  # processing | processed | flagged
    uploaded_at = Column(DateTime, default=utcnow)

    application = relationship("Application", back_populates="documents")


class Decision(Base):
    __tablename__ = "decisions"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), unique=True, nullable=False)
    decision_type = Column(String)
    # auto_approve | auto_decline | referred | manual_approve | manual_decline | request_more_info

    reasons = Column(JSON, nullable=True)       # list of reason strings
    shap_values = Column(JSON, nullable=True)   # dict of factor -> contribution
    adverse_action_codes = Column(JSON, nullable=True)

    notes = Column(Text, nullable=True)
    decided_by = Column(String, default="ai")

    # Manual override fields
    final_rate = Column(Float, nullable=True)
    final_amount = Column(Float, nullable=True)
    final_term_months = Column(Integer, nullable=True)

    decided_at = Column(DateTime, default=utcnow)

    application = relationship("Application", back_populates="decision")


class Offer(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    product_type = Column(String)   # term_loan | line_of_credit | sba_loan
    rate = Column(Float)            # APR %
    term_months = Column(Integer)
    amount = Column(Float)
    monthly_payment = Column(Float)
    created_at = Column(DateTime, default=utcnow)

    application = relationship("Application", back_populates="offers")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=True)
    event_type = Column(String)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=utcnow)

    application = relationship("Application", back_populates="audit_logs")


class ThresholdConfig(Base):
    __tablename__ = "threshold_configs"

    id = Column(Integer, primary_key=True, index=True)
    auto_approve_min = Column(Integer, default=700)
    auto_decline_max = Column(Integer, default=400)
    max_loan_amount = Column(Float, default=500000.0)
    min_years_in_business = Column(Float, default=1.0)
    updated_by = Column(String, default="system")
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    # Pending update (maker-checker workflow)
    pending_approve_min = Column(Integer, nullable=True)
    pending_decline_max = Column(Integer, nullable=True)
    pending_requested_by = Column(String, nullable=True)
    pending_approved_by = Column(String, nullable=True)
