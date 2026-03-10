from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime


# Application Schemas
class ApplicationCreate(BaseModel):
    applicant_name: Optional[str] = None
    applicant_email: Optional[str] = None
    applicant_phone: Optional[str] = None
    business_name: Optional[str] = None
    business_type: Optional[str] = None
    ein: Optional[str] = None
    years_in_business: Optional[float] = None
    industry: Optional[str] = None
    state: Optional[str] = None
    annual_revenue: Optional[float] = None
    monthly_expenses: Optional[float] = None
    credit_score: Optional[int] = None
    existing_debt: Optional[float] = None
    loan_amount: Optional[float] = None
    loan_purpose: Optional[str] = None


class ApplicationUpdate(ApplicationCreate):
    pass


class ApplicationResponse(BaseModel):
    id: int
    session_id: str
    applicant_name: Optional[str]
    applicant_email: Optional[str]
    applicant_phone: Optional[str]
    business_name: Optional[str]
    business_type: Optional[str]
    ein: Optional[str]
    years_in_business: Optional[float]
    industry: Optional[str]
    state: Optional[str]
    annual_revenue: Optional[float]
    monthly_expenses: Optional[float]
    credit_score: Optional[int]
    existing_debt: Optional[float]
    loan_amount: Optional[float]
    loan_purpose: Optional[str]
    bank_connected: bool
    avg_bank_balance: Optional[float]
    nsf_count: int
    monthly_deposits_avg: Optional[float]
    health_score: Optional[int]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Document Schemas
class DocumentResponse(BaseModel):
    id: int
    application_id: int
    doc_type: str
    filename: str
    file_size: int
    tamper_score: float
    extracted_data: Optional[Dict[str, Any]]
    status: str
    uploaded_at: datetime

    class Config:
        from_attributes = True


# Decision Schemas
class DecisionResponse(BaseModel):
    id: int
    application_id: int
    decision_type: str
    reasons: Optional[List[str]]
    shap_values: Optional[Dict[str, float]]
    adverse_action_codes: Optional[List[str]]
    notes: Optional[str]
    decided_by: str
    final_rate: Optional[float]
    final_amount: Optional[float]
    final_term_months: Optional[int]
    decided_at: datetime

    class Config:
        from_attributes = True


class ManualDecisionCreate(BaseModel):
    decision_type: str   # manual_approve | manual_decline | request_more_info
    notes: Optional[str] = None
    final_rate: Optional[float] = None
    final_amount: Optional[float] = None
    final_term_months: Optional[int] = None
    decline_reasons: Optional[List[str]] = None
    decided_by: str = "Underwriter"


# Offer Schemas
class OfferResponse(BaseModel):
    id: int
    application_id: int
    product_type: str
    rate: float
    term_months: int
    amount: float
    monthly_payment: float
    created_at: datetime

    class Config:
        from_attributes = True


# Audit Log
class AuditLogResponse(BaseModel):
    id: int
    application_id: Optional[int]
    event_type: str
    details: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


# Threshold Config
class ThresholdConfigResponse(BaseModel):
    id: int
    auto_approve_min: int
    auto_decline_max: int
    max_loan_amount: float
    min_years_in_business: float
    updated_by: str
    updated_at: datetime
    pending_approve_min: Optional[int]
    pending_decline_max: Optional[int]
    pending_requested_by: Optional[str]
    pending_approved_by: Optional[str]

    class Config:
        from_attributes = True


class ThresholdUpdateRequest(BaseModel):
    auto_approve_min: int
    auto_decline_max: int
    max_loan_amount: Optional[float] = None
    min_years_in_business: Optional[float] = None
    requested_by: str = "Risk Admin"


class ThresholdApprovalRequest(BaseModel):
    approved_by: str = "Risk Manager"


# Compliance / Analytics
class ComplianceMetrics(BaseModel):
    total_applications: int
    auto_approved: int
    auto_declined: int
    referred: int
    fraud_hold: int
    approval_rate: float
    avg_health_score: float
    by_business_type: Dict[str, Any]
    by_industry: Dict[str, Any]
    score_distribution: List[Dict[str, Any]]
