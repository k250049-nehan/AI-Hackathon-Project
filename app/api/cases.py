"""Case lifecycle, intake, review queue, dashboards and the mock scam map."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.ai.agent import run_agent
from app.ai.guardrails import requires_human_approval
from app.ai.structured import validate_claim
from app.audit import log
from app.db import get_db
from app.errors import AppError
from app.models import Case, Document, User
from app.schemas import (
    AgentRunOut,
    CaseAssign,
    CaseCreate,
    CaseEscalate,
    CaseOut,
    CaseReview,
    DashboardOut,
    DocumentCreate,
    DocumentOut,
    ExplainOut,
)
from app.security import enforce_consent, get_current_user, require_roles
from app.services import mock_payment, notifications, webhooks
from app.services.cases import create_case

from app.api.helpers import accessible_case_ids, actor_label, enforce_usage_limit, load_case

router = APIRouter(prefix="/api", tags=["cases"])


def _redact_for_auditor(case: Case) -> Case:
    """Return a copy with citizen-entered content removed for read-only audit."""
    return Case(
        id=case.id,
        tenant_id=case.tenant_id,
        case_number=case.case_number,
        case_type=case.case_type,
        subject_user_id=case.subject_user_id,
        created_by=case.created_by,
        assigned_to=case.assigned_to,
        status=case.status,
        priority=case.priority,
        confidence=case.confidence,
        jev_label=case.jev_label,
        decision=case.decision,
        decision_reason_simple=case.decision_reason_simple,
        decision_trace=case.decision_trace,
        officer_decision=case.officer_decision,
        officer_note=case.officer_note,
        reviewed_by=case.reviewed_by,
        reviewed_at=case.reviewed_at,
        payment_mock=case.payment_mock,
        rule_set_id=case.rule_set_id,
        raw_text=None,
        district=case.district,
        claim_data={},
        risk_flag=case.risk_flag,
        intake_channel=case.intake_channel,
        created_at=case.created_at,
        updated_at=case.updated_at,
        closed_at=case.closed_at,
    )


def _as_out(case: Case, actor: User) -> CaseOut:
    if actor.role == "auditor":
        case = _redact_for_auditor(case)
    return CaseOut.model_validate(case)


@router.post("/cases", response_model=CaseOut, status_code=201, summary="Create a claim / report")
def create_new_case(
    payload: CaseCreate,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> CaseOut:
    if actor.role not in {"citizen", "helper", "officer", "admin"}:
        raise AppError(403, "role_denied", "Your role cannot create cases.")
    subject = payload.subject_user_id or actor.id
    subject_user = db.get(User, subject)
    if not subject_user or subject_user.tenant_id != actor.tenant_id:
        raise AppError(404, "not_found", "Subject user not found in your workspace.")

    if subject != actor.id:
        enforce_consent(db, actor, subject, "relief_claim_assist", "submit_claim")

    claim_dict: dict = {}
    if payload.claim_data:
        validation = validate_claim(payload.claim_data.model_dump())
        if not validation["valid"]:
            raise AppError(422, "invalid_claim", "Structured claim failed validation.", {"errors": validation["errors"]})
        claim_dict = validation["data"]

    enforce_usage_limit(db, actor.tenant_id)
    case = create_case(
        db,
        tenant_id=actor.tenant_id,
        subject_user_id=subject,
        created_by=actor.id,
        case_type=payload.case_type,
        raw_text=payload.raw_text,
        claim_data=claim_dict,
        intake_channel=payload.intake_channel,
        district=payload.district,
    )
    db.commit()
    return _as_out(case, actor)


@router.get("/cases", response_model=list[CaseOut], summary="List cases visible to you")
def list_cases(
    limit: int = Query(default=50, ge=1, le=200),
    status: str | None = None,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> list[CaseOut]:
    ids = accessible_case_ids(db, actor)
    cases = [db.get(Case, case_id) for case_id in ids]
    if status:
        cases = [case for case in cases if case.status == status]
    return [_as_out(case, actor) for case in cases[:limit]]


@router.get("/cases/{case_id}", response_model=CaseOut, summary="Read one case")
def get_case(
    case_id: str,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> CaseOut:
    case = load_case(db, case_id, actor)
    return _as_out(case, actor)


@router.post("/cases/{case_id}/assign", response_model=CaseOut, summary="Assign a case to an officer")
def assign_case(
    case_id: str,
    payload: CaseAssign,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles("officer", "admin")),
) -> CaseOut:
    case = load_case(db, case_id, actor)
    assignee = db.get(User, payload.assignee_user_id)
    if not assignee or assignee.tenant_id != actor.tenant_id or assignee.role not in {"officer", "helper"}:
        raise AppError(404, "not_found", "Assignee not found in your workspace.")
    case.assigned_to = assignee.id
    case.status = "assigned"
    log(
        db,
        tenant_id=actor.tenant_id,
        actor_type="user",
        actor_id=actor.id,
        action="case.assigned",
        target_type="case",
        target_id=case.id,
        detail={"assignee": assignee.id, "role": assignee.role},
    )
    notifications.notify(
        db,
        tenant_id=actor.tenant_id,
        user_id=assignee.id,
        title="Case assigned / کیس تفویض",
        body=f"Case {case.case_number} was assigned to you.",
        actor_id=actor.id,
    )
    db.commit()
    return CaseOut.model_validate(case)


@router.post("/cases/{case_id}/escalate", response_model=CaseOut, summary="Escalate to a senior reviewer")
def escalate_case(
    case_id: str,
    payload: CaseEscalate,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> CaseOut:
    case = load_case(db, case_id, actor, purpose="relief_claim_assist", scope="read_claim")
    case.status = "escalated"
    case.priority = "high"
    log(
        db,
        tenant_id=actor.tenant_id,
        actor_type="user",
        actor_id=actor.id,
        action="case.escalated",
        target_type="case",
        target_id=case.id,
        detail={"reason": payload.reason, "actor_role": actor.role},
    )
    db.commit()
    return _as_out(case, actor)


@router.post("/cases/{case_id}/review", response_model=CaseOut, summary="Officer decision (approval gate)")
def review_case(
    case_id: str,
    payload: CaseReview,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles("officer", "admin")),
) -> CaseOut:
    case = load_case(db, case_id, actor, purpose="department_review", scope="review_claim")
    needed, approval_reason = requires_human_approval(
        "approve_claim", case.confidence, (case.decision_trace or {}).get("thresholds")
    )
    if not needed:
        raise AppError(409, "review_not_required", "This case does not need an officer decision.")

    case.officer_decision = payload.decision
    case.officer_note = payload.note
    case.reviewed_by = actor.id
    case.reviewed_at = datetime.now(timezone.utc)
    case.assigned_to = case.assigned_to or actor.id

    if payload.decision == "approved":
        case.status = "approved"
        payment = mock_payment.disburse(
            case.case_number,
            float((case.claim_data or {}).get("claim_amount", 0)),
            approved_by=actor.id,
        )
        case.payment_mock = payment
    elif payload.decision == "rejected":
        case.status = "rejected"
    else:
        case.status = "needs_info"

    log(
        db,
        tenant_id=actor.tenant_id,
        actor_type="user",
        actor_id=actor.id,
        action="case.reviewed",
        target_type="case",
        target_id=case.id,
        detail={
            "decision": payload.decision,
            "note": payload.note,
            "rule_version": (case.decision_trace or {}).get("rule_version"),
            "ai_decision": case.decision,
            "simulated_payment": bool(case.payment_mock),
        },
    )
    notifications.notify(
        db,
        tenant_id=actor.tenant_id,
        user_id=case.subject_user_id,
        title="Decision on your case / آپ کی درخواست کا فیصلہ",
        body=f"Case {case.case_number}: {payload.decision}.",
        actor_id=actor.id,
    )
    webhooks.dispatch(
        db,
        tenant_id=actor.tenant_id,
        event="case.decided",
        payload={"case_id": case.id, "decision": payload.decision, "mock": True},
    )
    db.commit()
    return CaseOut.model_validate(case)


@router.post("/cases/{case_id}/close", response_model=CaseOut, summary="Close a decided case")
def close_case(
    case_id: str,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles("officer", "admin")),
) -> CaseOut:
    case = load_case(db, case_id, actor, purpose="department_review", scope="review_claim")
    if case.status not in {"approved", "rejected", "blocked"}:
        raise AppError(409, "invalid_state", "Only decided cases can be closed.")
    case.status = "closed"
    case.closed_at = datetime.now(timezone.utc)
    log(
        db,
        tenant_id=actor.tenant_id,
        actor_type="user",
        actor_id=actor.id,
        action="case.closed",
        target_type="case",
        target_id=case.id,
        detail={"final_decision": case.officer_decision or case.decision},
    )
    db.commit()
    return CaseOut.model_validate(case)


@router.post("/cases/{case_id}/documents", response_model=DocumentOut, status_code=201)
def add_document(
    case_id: str,
    payload: DocumentCreate,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> DocumentOut:
    case = load_case(db, case_id, actor, purpose="relief_claim_assist", scope="submit_claim")
    if payload.owner_user_id != case.subject_user_id:
        raise AppError(403, "consent_required", "Document owner must be the case subject.")
    document = Document(
        tenant_id=actor.tenant_id,
        case_id=case.id,
        owner_user_id=payload.owner_user_id,
        doc_type=payload.doc_type,
        file_name=payload.file_name,
        ocr_text=payload.ocr_text,
        qr_valid=payload.qr_valid,
        forgery_score=payload.forgery_score or 0.0,
        is_mock=True,
    )
    db.add(document)
    db.flush()
    log(
        db,
        tenant_id=actor.tenant_id,
        actor_type="user",
        actor_id=actor.id,
        action="document.added",
        target_type="document",
        target_id=document.id,
        detail={"case_id": case.id, "doc_type": payload.doc_type, "simulated": True},
    )
    db.commit()
    return DocumentOut.model_validate(document)


@router.get("/cases/{case_id}/explain", response_model=ExplainOut, summary="Citizen + auditor explanations")
def explain_case(
    case_id: str,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> ExplainOut:
    case = load_case(db, case_id, actor)
    explanation = (case.decision_trace or {}).get("explanation") or {}
    return ExplainOut(
        simple=explanation.get("simple", case.decision_reason_simple or "No explanation available."),
        simple_urdu=explanation.get("simple_urdu", "کوئی وضاحت دستیاب نہیں۔"),
        audit_trace=explanation.get("audit_trace", case.decision_trace or {}),
    )


@router.post("/cases/{case_id}/agent/run", response_model=AgentRunOut, summary="Run the mock tool-calling agent")
def run_case_agent(
    case_id: str,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles("officer", "admin", "helper")),
) -> AgentRunOut:
    if actor.role == "helper":
        case = load_case(db, case_id, actor, purpose="relief_claim_assist", scope="read_claim")
    else:
        case = load_case(db, case_id, actor, purpose="department_review", scope="review_claim")
    result = run_agent(db, case, actor)
    db.commit()
    return AgentRunOut(**result)


@router.get("/dashboard", response_model=DashboardOut, summary="Task progress, status and history")
def dashboard(
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> DashboardOut:
    ids = accessible_case_ids(db, actor)
    cases = [db.get(Case, case_id) for case_id in ids]
    return DashboardOut(
        tenant_id=actor.tenant_id,
        role=actor.role,
        total_cases=len(cases),
        by_status=dict(Counter(case.status for case in cases)),
        by_type=dict(Counter(case.case_type for case in cases)),
        recent_cases=[_as_out(case, actor) for case in cases[:5]],
    )


@router.get("/officer/queue", summary="Officer review queue sorted by priority and confidence")
def officer_queue(
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles("officer", "admin")),
) -> list[dict]:
    cases = [
        db.get(Case, case_id)
        for case_id in accessible_case_ids(db, actor)
    ]
    pending = [case for case in cases if case.status in {"new", "assigned", "needs_info", "human_review", "pending_officer"}]
    pending.sort(key=lambda case: (0 if case.priority == "high" else 1, case.confidence))
    return [
        {
            "case_id": case.id,
            "case_number": case.case_number,
            "status": case.status,
            "priority": case.priority,
            "confidence": case.confidence,
            "ai_decision": case.decision,
            "reason": case.decision_reason_simple,
            "rule_version": (case.decision_trace or {}).get("rule_version"),
            "simulated": True,
        }
        for case in pending
    ]


@router.get("/scam-map", summary="Mock scam pattern map by district and day")
def scam_map(
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> dict:
    ids = accessible_case_ids(db, actor)
    cases = [db.get(Case, case_id) for case_id in ids]
    cases = [case for case in cases if case.case_type == "scam_report"]
    by_district = Counter(case.district or "unknown" for case in cases)
    by_label = Counter(case.jev_label or "unknown" for case in cases)
    by_day = Counter(
        case.created_at.strftime("%Y-%m-%d") if case.created_at else "unknown" for case in cases
    )
    return {
        "total_reports": len(cases),
        "by_district": dict(by_district),
        "by_label": dict(by_label),
        "by_day": dict(by_day),
        "simulated": True,
    }
