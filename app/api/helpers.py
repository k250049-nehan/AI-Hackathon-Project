"""Shared helpers for API routers."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.errors import AppError
from app.models import Case, Consent, Tenant, User
from app.security import enforce_consent

PLAN_LIMITS = {"free": 50, "team": 10000, "enterprise": 1000000}


def actor_label(actor: User) -> str:
    return f"{actor.role}:{actor.id}"


def load_case(
    db: Session,
    case_id: str,
    actor: User,
    *,
    purpose: str = "department_review",
    scope: str = "read_claim",
) -> Case:
    case = db.get(Case, case_id)
    if not case or case.tenant_id != actor.tenant_id:
        raise AppError(404, "not_found", "Case not found.")
    # Auditors read redacted metadata and AI decision traces only.
    if actor.role != "auditor":
        enforce_consent(db, actor, case.subject_user_id, purpose, scope)
    return case


def accessible_case_ids(db: Session, actor: User) -> list[str]:
    """Case ids the actor is allowed to see, computed with server-side consent."""
    cases = db.scalars(
        select(Case).where(Case.tenant_id == actor.tenant_id).order_by(Case.created_at.desc())
    ).all()
    if actor.role in {"admin", "officer"}:
        return [case.id for case in cases]
    result = []
    for case in cases:
        if actor.role == "auditor":
            result.append(case.id)  # metadata only; claim data is redacted in responses
            continue
        if case.created_by == actor.id:
            result.append(case.id)
            continue
        grant = db.scalar(
            select(Consent).where(
                Consent.subject_user_id == case.subject_user_id,
                Consent.grantee_user_id == actor.id,
                Consent.status == "active",
            )
        )
        if grant:
            result.append(case.id)
    return result


def enforce_usage_limit(db: Session, tenant_id: str) -> None:
    tenant = db.get(Tenant, tenant_id)
    if not tenant:
        raise AppError(404, "not_found", "Workspace not found.")
    limit = PLAN_LIMITS.get(tenant.plan, PLAN_LIMITS["free"])
    used = db.query(Case).filter(Case.tenant_id == tenant_id).count()
    if used >= limit:
        raise AppError(
            429,
            "usage_limit_reached",
            f"The {tenant.plan} plan allows {limit} cases. Upgrade to add more.",
        )
