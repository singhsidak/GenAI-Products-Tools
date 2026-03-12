"""Pydantic schemas matching frontend TypeScript interfaces."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# ── Auth ──────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    message: str
    user: "UserOut"


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: str
    is_active: bool
    force_password_change: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ── Runs ──────────────────────────────────────────────────────────────────────

class RunListItem(BaseModel):
    id: int
    run_id: str
    run_name: str
    study_id: str
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    duration_minutes: Optional[float] = None
    initiated_by_username: str
    total_cost_usd: Optional[float] = None
    total_tokens: Optional[int] = None
    completed_sections: Optional[int] = None
    failed_sections: Optional[int] = None
    total_sections: Optional[int] = None
    total_tokens_used: Optional[int] = None


class RunDetailOut(BaseModel):
    id: int
    run_id: str
    study_id: str
    run_name: str
    status: str
    current_phase: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    initiated_by: int
    total_input_tokens: Optional[int] = None
    total_output_tokens: Optional[int] = None
    total_cost_usd: Optional[float] = None
    error_message: Optional[str] = None
    parent_run_id: Optional[str] = None
    completed_sections: int
    failed_sections: int
    total_sections: int
    total_tokens_used: int


class RerunRequest(BaseModel):
    scope: Optional[str] = None
    section_number: Optional[int] = None
    replace_documents: Optional[bool] = False


# ── Sections ──────────────────────────────────────────────────────────────────

class SectionSummary(BaseModel):
    id: int
    run_id: str
    section_number: int
    section_name: str
    title: str
    agent_name: str
    status: str
    word_count: Optional[int] = None
    is_human_edited: bool
    is_edited: bool
    retry_count: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    edited_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SectionDetailOut(SectionSummary):
    content: Optional[str] = None
    compliance_trace: Optional[list] = None
    data_not_available_count: int = 0
    gcp_deviation_count: int = 0
    tokens_used: Optional[int] = None
    generation_cost_usd: Optional[float] = None
    edit_count: Optional[int] = 0


class SectionUpdateRequest(BaseModel):
    content: str


# ── Compliance ────────────────────────────────────────────────────────────────

class ComplianceReportOut(BaseModel):
    id: int
    run_id: str
    version_id: str
    overall_status: str
    data_not_available_count: int
    gcp_deviation_count: int
    report_content: Optional[dict] = None
    is_signed: bool
    signed_by_username: Optional[str] = None
    signed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ComplianceSignRequest(BaseModel):
    acknowledged: bool


class ComplianceAuditOut(BaseModel):
    id: int
    user_id: int
    username: str
    action: str
    timestamp: datetime

    class Config:
        from_attributes = True


# ── Agent Logs ────────────────────────────────────────────────────────────────

class AgentLogOut(BaseModel):
    id: int
    agent_name: str
    phase: Optional[str] = None
    status: str
    message: Optional[str] = None
    timestamp: datetime
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    estimated_cost_usd: Optional[float] = None

    class Config:
        from_attributes = True


# ── Notifications ─────────────────────────────────────────────────────────────

class NotificationOut(BaseModel):
    id: int
    run_id: Optional[str] = None
    event_type: str
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationPrefOut(BaseModel):
    event_type: str
    is_enabled: bool


class NotificationPrefUpdate(BaseModel):
    event_type: str
    is_enabled: bool


# ── Admin ─────────────────────────────────────────────────────────────────────

class CreateUserRequest(BaseModel):
    username: str
    email: str
    temp_password: str
    role: str
    full_name: str


class UpdateUserRequest(BaseModel):
    is_active: Optional[bool] = None
    role: Optional[str] = None
    full_name: Optional[str] = None


# ── Dashboard ─────────────────────────────────────────────────────────────────

class AnalyticsSummary(BaseModel):
    period: str
    total_runs: int
    completed_runs: int
    failed_runs: int
    total_cost_usd: float
    avg_cost_per_run_usd: float
    total_tokens: int
    total_tokens_used: int
    runs_by_status: dict
    avg_completion_minutes: Optional[float] = None
    compliance_pass_rate: Optional[float] = None
