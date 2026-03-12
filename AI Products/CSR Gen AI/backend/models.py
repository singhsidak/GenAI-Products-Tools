"""SQLAlchemy ORM models."""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
)
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(200), unique=True, nullable=False)
    full_name = Column(String(200), nullable=False, default="")
    hashed_password = Column(String(256), nullable=False)
    role = Column(String(20), nullable=False, default="user")  # admin, reviewer, user
    is_active = Column(Boolean, default=True)
    force_password_change = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    runs = relationship("Run", back_populates="initiated_by_user")
    notifications = relationship("Notification", back_populates="user")


class Run(Base):
    __tablename__ = "runs"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String(20), unique=True, nullable=False, index=True)
    run_name = Column(String(200), nullable=False, default="")
    study_id = Column(String(100), nullable=False, default="")
    status = Column(String(30), nullable=False, default="pending")
    current_phase = Column(String(100), nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    initiated_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    error_message = Column(Text, nullable=True)
    parent_run_id = Column(String(20), nullable=True)
    total_input_tokens = Column(Integer, default=0)
    total_output_tokens = Column(Integer, default=0)
    total_cost_usd = Column(Float, default=0.0)

    initiated_by_user = relationship("User", back_populates="runs")
    sections = relationship("Section", back_populates="run", cascade="all, delete-orphan")
    documents = relationship("RunDocument", back_populates="run", cascade="all, delete-orphan")
    logs = relationship("AgentLog", back_populates="run", cascade="all, delete-orphan")
    compliance_reports = relationship("ComplianceReport", back_populates="run", cascade="all, delete-orphan")
    output_files = relationship("OutputFile", back_populates="run", cascade="all, delete-orphan")

    @property
    def completed_sections(self):
        return sum(1 for s in self.sections if s.status == "completed")

    @property
    def failed_sections(self):
        return sum(1 for s in self.sections if s.status == "failed")

    @property
    def total_sections(self):
        return len(self.sections)

    @property
    def total_tokens_used(self):
        return (self.total_input_tokens or 0) + (self.total_output_tokens or 0)

    @property
    def duration_minutes(self):
        if self.started_at and self.completed_at:
            return round((self.completed_at - self.started_at).total_seconds() / 60, 1)
        return None


class RunDocument(Base):
    __tablename__ = "run_documents"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String(20), ForeignKey("runs.run_id"), nullable=False)
    zone = Column(String(10), nullable=False)  # A, B, C
    original_filename = Column(String(500), nullable=False)
    stored_path = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer, nullable=True)
    upload_status = Column(String(20), default="uploaded")
    created_at = Column(DateTime, default=datetime.utcnow)

    run = relationship("Run", back_populates="documents", foreign_keys=[run_id],
                        primaryjoin="RunDocument.run_id == Run.run_id")


class Section(Base):
    __tablename__ = "sections"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String(20), ForeignKey("runs.run_id"), nullable=False)
    section_number = Column(Integer, nullable=False)
    section_name = Column(String(200), nullable=False)
    agent_name = Column(String(100), nullable=False, default="")
    status = Column(String(30), nullable=False, default="pending")
    content = Column(Text, nullable=True)
    word_count = Column(Integer, nullable=True)
    is_human_edited = Column(Boolean, default=False)
    retry_count = Column(Integer, default=0)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    edited_at = Column(DateTime, nullable=True)
    compliance_trace = Column(JSON, nullable=True)
    data_not_available_count = Column(Integer, default=0)
    gcp_deviation_count = Column(Integer, default=0)
    tokens_used = Column(Integer, nullable=True)
    generation_cost_usd = Column(Float, nullable=True)

    run = relationship("Run", back_populates="sections",
                        foreign_keys=[run_id],
                        primaryjoin="Section.run_id == Run.run_id")


class AgentLog(Base):
    __tablename__ = "agent_logs"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String(20), ForeignKey("runs.run_id"), nullable=False)
    agent_name = Column(String(100), nullable=False)
    phase = Column(String(100), nullable=True)
    status = Column(String(30), nullable=False)
    message = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    input_tokens = Column(Integer, nullable=True)
    output_tokens = Column(Integer, nullable=True)
    estimated_cost_usd = Column(Float, nullable=True)

    run = relationship("Run", back_populates="logs",
                        foreign_keys=[run_id],
                        primaryjoin="AgentLog.run_id == Run.run_id")


class ComplianceReport(Base):
    __tablename__ = "compliance_reports"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String(20), ForeignKey("runs.run_id"), nullable=False)
    version_id = Column(String(50), nullable=False)
    overall_status = Column(String(30), nullable=False, default="pending")
    data_not_available_count = Column(Integer, default=0)
    gcp_deviation_count = Column(Integer, default=0)
    report_content = Column(JSON, nullable=True)
    is_signed = Column(Boolean, default=False)
    signed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    signed_by_username = Column(String(80), nullable=True)
    signed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    run = relationship("Run", back_populates="compliance_reports",
                        foreign_keys=[run_id],
                        primaryjoin="ComplianceReport.run_id == Run.run_id")


class ComplianceAudit(Base):
    __tablename__ = "compliance_audits"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String(20), ForeignKey("runs.run_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    username = Column(String(80), nullable=False)
    action = Column(String(200), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    run_id = Column(String(20), nullable=True)
    event_type = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")


class NotificationPreference(Base):
    __tablename__ = "notification_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_type = Column(String(50), nullable=False)
    is_enabled = Column(Boolean, default=True)


class OutputFile(Base):
    __tablename__ = "output_files"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String(20), ForeignKey("runs.run_id"), nullable=False)
    file_type = Column(String(20), nullable=False)  # pdf, docx, index_csv
    stored_path = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    run = relationship("Run", back_populates="output_files",
                        foreign_keys=[run_id],
                        primaryjoin="OutputFile.run_id == Run.run_id")
