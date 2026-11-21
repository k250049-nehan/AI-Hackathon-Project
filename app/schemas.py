"""Pydantic request/response contracts (also used for structured AI outputs)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.normalization import normalize_cnic, normalize_name, safe_text


class APIModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")


class PrototypeNotice(BaseModel):
    prototype: bool = True
    official_service: bool = False
    real_personal_data: bool = False
    notice: str = "PROTOTYPE - NOT AN OFFICIAL SERVICE - ALL DATA MOCKED"


# ---------------------------------------------------------------------------
# Auth & users
# ---------------------------------------------------------------------------

class LoginRequest(APIModel):
    email: str = Field(max_length=200)
    password: str = Field(max_length=200)


class TokenResponse(APIModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    tenant_id: str
    role: str
    prototype: PrototypeNotice = Field(default_factory=PrototypeNotice)


class UserCreate(APIModel):
    email: str = Field(max_length=200)
    full_name: str = Field(max_length=200)
    password: str = Field(min_length=6, max_length=200)
    role: Literal["citizen", "helper", "officer", "admin", "auditor"]
    phone: str | None = None
    preferred_language: str = "ur"


class UserOut(APIModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    email: str
    full_name: str
    role: str
    phone: str | None
    preferred_language: str
    is_active: bool
    created_at: datetime


class ApiKeyCreate(APIModel):
    name: str = Field(max_length=120)
    scopes: list[str] = Field(default_factory=lambda: ["cases:read", "cases:write"])


class ApiKeyOut(APIModel):
    id: str
    name: str
    prefix: str
    plain_key: str
    scopes: list[str]


# ---------------------------------------------------------------------------
# Structured claim form & cases
# ---------------------------------------------------------------------------

class ClaimForm(APIModel):
    """Structured output contract for a relief-payment claim."""

    full_name: str = Field(min_length=2, max_length=200)
    cnic: str = Field(max_length=20)
    category: Literal["widow", "disabled", "unemployed", "low_income"] = "low_income"
    monthly_income: int = Field(ge=0, le=10_000_000)
    dependents: int = Field(ge=0, le=30, default=0)
    claim_amount: int = Field(gt=0, le=1_000_000)
    district: str = Field(min_length=2, max_length=80)

    @field_validator("full_name", mode="before")
    @classmethod
    def clean_name(cls, value: Any) -> str:
        return normalize_name(safe_text(value, 200))

    @field_validator("cnic", mode="before")
    @classmethod
    def clean_cnic(cls, value: Any) -> str:
        digits = normalize_cnic(safe_text(value, 30))
        if not digits:
            raise ValueError("CNIC must contain exactly 13 digits")
        return digits

    @field_validator("district", mode="before")
    @classmethod
    def clean_district(cls, value: Any) -> str:
        return safe_text(value, 80).strip().title()

    @model_validator(mode="after")
    def check_amount_vs_income(self) -> "ClaimForm":
        if self.claim_amount > max(self.monthly_income * 3, 5000):
            raise ValueError("claim_amount is too high for the declared income")
        return self


class CaseCreate(APIModel):
    case_type: Literal["relief_claim", "scam_report", "complaint"] = "relief_claim"
    subject_user_id: str | None = None
    raw_text: str | None = Field(default=None, max_length=4000)
    claim_data: ClaimForm | None = None
    intake_channel: Literal["text", "voice", "helper", "offline"] = "text"
    district: str | None = None
    client_id: str | None = None
    op_id: str | None = None


class VoiceIntakeRequest(APIModel):
    transcript: str = Field(min_length=1, max_length=4000)
    language: str = "ur"
    subject_user_id: str | None = None
    audio_transcribed_by: str = "browser_web_speech_api"
    claim_data: dict[str, Any] | None = None


class CaseAssign(APIModel):
    assignee_user_id: str


class CaseReview(APIModel):
    decision: Literal["approved", "rejected", "needs_info"]
    note: str = Field(default="", max_length=2000)


class CaseEscalate(APIModel):
    reason: str = Field(min_length=3, max_length=1000)


class CaseOut(APIModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    case_number: str
    case_type: str
    subject_user_id: str
    created_by: str
    assigned_to: str | None
    status: str
    priority: str
    confidence: float
    jev_label: str | None
    decision: str | None
    decision_reason_simple: str | None
    decision_trace: dict
    officer_decision: str | None
    officer_note: str | None
    reviewed_by: str | None
    reviewed_at: datetime | None
    payment_mock: dict
    rule_set_id: str | None
    raw_text: str | None
    district: str | None
    claim_data: dict
    risk_flag: str | None
    intake_channel: str
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None
    prototype: PrototypeNotice = Field(default_factory=PrototypeNotice)


class DashboardOut(APIModel):
    tenant_id: str
    role: str
    total_cases: int
    by_status: dict[str, int]
    by_type: dict[str, int]
    recent_cases: list[CaseOut]


# ---------------------------------------------------------------------------
# Rules & digital twin
# ---------------------------------------------------------------------------

class RuleDefinition(APIModel):
    max_income: int = 30000
    min_income: int = 0
    max_claim_amount: int = 25000
    allowed_categories: list[str] = Field(
        default_factory=lambda: ["widow", "disabled", "unemployed", "low_income"]
    )
    required_documents: list[str] = Field(default_factory=lambda: ["cnic"])
    auto_approve_min_confidence: float = 0.90
    ask_info_min_confidence: float = 0.65
    scam_block_confidence: float = 0.85
    duplicate_window_days: int = 30
    max_duplicate_claims: int = 1
    require_officer_for_payment: bool = True
    note: str = ""


class RuleCreate(APIModel):
    name: str = "relief_eligibility"
    definition: RuleDefinition
    change_note: str = ""


class RuleOut(APIModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    name: str
    version: int
    definition: dict
    is_active: bool
    change_note: str | None
    created_at: datetime


class DigitalTwinRequest(APIModel):
    definition: RuleDefinition
    case_ids: list[str] | None = None


# ---------------------------------------------------------------------------
# Consent, audit, documents
# ---------------------------------------------------------------------------

class ConsentCreate(APIModel):
    subject_user_id: str
    grantee_user_id: str | None = None
    grantee_role: str | None = None
    purpose: Literal[
        "relief_claim_assist", "department_review", "data_share", "notifications"
    ]
    scopes: list[str] = Field(default_factory=lambda: ["read_profile", "read_claim"])
    action: Literal["grant", "withdraw"] = "grant"


class ConsentOut(APIModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    subject_user_id: str
    grantee_user_id: str | None
    grantee_role: str | None
    purpose: str
    scopes: list[str]
    status: str
    updated_at: datetime


class AuditOut(APIModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    actor_type: str
    actor_id: str
    action: str
    target_type: str | None
    target_id: str | None
    detail: dict
    created_at: datetime


class DocumentCreate(APIModel):
    owner_user_id: str
    case_id: str | None = None
    doc_type: Literal["cnic", "proof_of_income", "income_certificate", "other"]
    file_name: str | None = None
    ocr_text: str | None = None
    qr_valid: bool | None = None
    forgery_score: float | None = Field(default=None, ge=0.0, le=1.0)


class DocumentOut(APIModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    case_id: str | None
    owner_user_id: str
    doc_type: str
    file_name: str | None
    ocr_text: str | None
    qr_valid: bool | None
    forgery_score: float
    is_mock: bool


# ---------------------------------------------------------------------------
# AI endpoints
# ---------------------------------------------------------------------------

class JevRequest(APIModel):
    text: str = Field(min_length=1, max_length=4000)
    case_id: str | None = None


class JevOut(APIModel):
    label: str
    confidence: float
    scores: dict[str, float]
    route: str
    reason: str
    model_version: str
    simulated: bool = True
    signal_groups: int | None = None
    latency_ms: float | None = None


class RAGRequest(APIModel):
    question: str = Field(min_length=2, max_length=1000)
    top_k: int = Field(default=3, ge=1, le=6)


class RagSource(APIModel):
    document: str
    section: str
    quote: str
    relevance: float


class RagOut(APIModel):
    answer: str
    sources: list[RagSource]
    simulated: bool = True
    uncertain: bool = False


class ExplainOut(APIModel):
    simple: str
    simple_urdu: str
    audit_trace: dict


class AgentStep(APIModel):
    step: str
    tool: str
    input: dict
    output: dict
    mock: bool = True


class AgentRunOut(APIModel):
    case_id: str
    plan: list[str]
    steps: list[AgentStep]
    final_decision: str
    human_approval_required: bool
    rule_version: int | None = None
    simulated: bool = True


# ---------------------------------------------------------------------------
# Operations: notifications, webhooks, sync, evaluation, public API
# ---------------------------------------------------------------------------

class NotificationOut(APIModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    user_id: str
    channel: str
    title: str
    body: str
    status: str


class WebhookCreate(APIModel):
    url: str = Field(max_length=500)
    event_types: list[str] = Field(default_factory=lambda: ["case.created", "case.decided"])


class WebhookOut(APIModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    url: str
    event_types: list[str]
    is_active: bool


class SyncOperationIn(APIModel):
    op_id: str = Field(min_length=1, max_length=80)
    op_type: Literal["create_case", "voice_intake", "scam_report"]
    payload: dict = Field(default_factory=dict)


class SyncRequest(APIModel):
    client_id: str = Field(min_length=2, max_length=80)
    operations: list[SyncOperationIn] = Field(default_factory=list, max_length=100)


class SyncResult(APIModel):
    client_id: str
    processed: int
    duplicates_skipped: int
    results: list[dict]


class EvaluationRecordIn(APIModel):
    case_id: str | None = None
    predicted_label: str
    actual_label: str
    confidence: float = Field(ge=0.0, le=1.0)
    latency_ms: float = Field(ge=0.0)
    notes: str | None = None


class PublicCaseCreate(APIModel):
    case_type: Literal["relief_claim", "scam_report", "complaint"] = "relief_claim"
    subject_user_id: str
    raw_text: str | None = None
    district: str | None = None
