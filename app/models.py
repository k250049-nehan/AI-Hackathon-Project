"""SQLAlchemy ORM models for the prototype.

All records are mock/simulated. No real personal data is stored.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Float, ForeignKey, Index, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db import Base


def new_id() -> str:
    return uuid.uuid4().hex


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    slug: Mapped[str] = mapped_column(String(80), nullable=False, unique=True, index=True)
    plan: Mapped[str] = mapped_column(String(32), nullable=False, default="free")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)


class User(Base):
    __tablename__ = "users"
    __table_args__ = (Index("ix_users_tenant_role", "tenant_id", "role"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(200), nullable=False, unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False, default="citizen")
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    preferred_language: Mapped[str] = mapped_column(String(16), default="ur")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    tenant: Mapped[Tenant] = relationship(lazy="joined")


class ApiKey(Base):
    __tablename__ = "api_keys"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    prefix: Mapped[str] = mapped_column(String(24), nullable=False, index=True)
    key_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    scopes: Mapped[list] = mapped_column(JSON, default=list)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    last_used_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)


class Consent(Base):
    __tablename__ = "consents"
    __table_args__ = (
        Index("ix_consent_subject_grantee", "subject_user_id", "grantee_user_id", "purpose"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    subject_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    grantee_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    grantee_role: Mapped[str | None] = mapped_column(String(40), nullable=True)
    purpose: Mapped[str] = mapped_column(String(80), nullable=False)
    scopes: Mapped[list] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)


class RuleSet(Base):
    __tablename__ = "rule_sets"
    __table_args__ = (
        Index("ix_rules_tenant_active", "tenant_id", "is_active"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, default="relief_eligibility")
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    definition: Mapped[dict] = mapped_column(JSON, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    created_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    change_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)


class Case(Base):
    __tablename__ = "cases"
    __table_args__ = (
        Index("ix_cases_tenant_status", "tenant_id", "status"),
        Index("ix_cases_subject", "tenant_id", "subject_user_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    case_number: Mapped[str] = mapped_column(String(40), nullable=False, unique=True, index=True)
    case_type: Mapped[str] = mapped_column(String(40), nullable=False, default="relief_claim")
    subject_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    created_by: Mapped[str] = mapped_column(String(36), nullable=False)
    assigned_to: Mapped[str | None] = mapped_column(String(36), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="new", index=True)
    priority: Mapped[str] = mapped_column(String(16), default="normal")
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    jev_label: Mapped[str | None] = mapped_column(String(40), nullable=True)
    jev_scores: Mapped[dict] = mapped_column(JSON, default=dict)
    decision: Mapped[str | None] = mapped_column(String(40), nullable=True)
    decision_reason_simple: Mapped[str | None] = mapped_column(Text, nullable=True)
    decision_trace: Mapped[dict] = mapped_column(JSON, default=dict)
    officer_decision: Mapped[str | None] = mapped_column(String(40), nullable=True)
    officer_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    payment_mock: Mapped[dict] = mapped_column(JSON, default=dict)
    rule_set_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    district: Mapped[str | None] = mapped_column(String(80), nullable=True)
    claim_data: Mapped[dict] = mapped_column(JSON, default=dict)
    risk_flag: Mapped[str | None] = mapped_column(String(40), nullable=True)
    intake_channel: Mapped[str] = mapped_column(String(20), default="text")
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)
    closed_at: Mapped[datetime | None] = mapped_column(nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = (Index("ix_audit_tenant_time", "tenant_id", "created_at"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    actor_type: Mapped[str] = mapped_column(String(20), nullable=False)
    actor_id: Mapped[str] = mapped_column(String(64), nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    target_type: Mapped[str | None] = mapped_column(String(60), nullable=True)
    target_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    detail: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    case_id: Mapped[str | None] = mapped_column(ForeignKey("cases.id"), nullable=True)
    owner_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    doc_type: Mapped[str] = mapped_column(String(40), nullable=False)
    file_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    ocr_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    qr_valid: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    forgery_score: Mapped[float] = mapped_column(Float, default=0.0)
    is_mock: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    channel: Mapped[str] = mapped_column(String(20), default="in_app")
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="queued")
    created_at: Mapped[datetime] = mapped_column(default=utcnow)


class Webhook(Base):
    __tablename__ = "webhooks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    event_types: Mapped[list] = mapped_column(JSON, default=list)
    secret: Mapped[str] = mapped_column(String(80), default="mock-webhook-secret")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)


class WebhookDelivery(Base):
    __tablename__ = "webhook_deliveries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    webhook_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    event: Mapped[str] = mapped_column(String(80), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(20), default="attempted")
    response_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)


class EvaluationRecord(Base):
    __tablename__ = "evaluation_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    case_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    predicted_label: Mapped[str] = mapped_column(String(40), nullable=False)
    actual_label: Mapped[str] = mapped_column(String(40), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    was_false_alarm: Mapped[bool] = mapped_column(Boolean, default=False)
    was_missed: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)


class SyncOperation(Base):
    __tablename__ = "sync_operations"
    __table_args__ = (
        Index("ix_sync_idempotency", "client_id", "op_id", unique=True),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    client_id: Mapped[str] = mapped_column(String(80), nullable=False)
    op_id: Mapped[str] = mapped_column(String(80), nullable=False)
    op_type: Mapped[str] = mapped_column(String(40), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    result: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)


class UsageCounter(Base):
    __tablename__ = "usage_counters"
    __table_args__ = (Index("ix_usage_tenant_period", "tenant_id", "period", unique=True),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    period: Mapped[str] = mapped_column(String(16), nullable=False)
    cases_created: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)
