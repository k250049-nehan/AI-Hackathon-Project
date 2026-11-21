"""Consent lifecycle: see, share, correct, and truly withdraw."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.errors import AppError
from app.models import Consent, User, new_id
from app.security import has_consent


def grant_consent(
    db: Session,
    *,
    tenant_id: str,
    subject_user_id: str,
    purpose: str,
    scopes: list[str],
    grantee_user_id: str | None = None,
    grantee_role: str | None = None,
) -> Consent:
    """Create or reactivate a consent grant, idempotently."""
    if grantee_user_id:
        grantee = db.get(User, grantee_user_id)
        if not grantee or grantee.tenant_id != tenant_id:
            raise AppError(404, "not_found", "Grantee user not found in your workspace.")

    existing = db.scalar(
        select(Consent).where(
            Consent.tenant_id == tenant_id,
            Consent.subject_user_id == subject_user_id,
            Consent.purpose == purpose,
            Consent.grantee_user_id.is_(grantee_user_id) if grantee_user_id else Consent.grantee_user_id.is_(None),
            Consent.grantee_role.is_(grantee_role) if grantee_role else Consent.grantee_role.is_(None),
        )
    )
    now = datetime.now(timezone.utc)
    if existing:
        existing.status = "active"
        existing.scopes = scopes
        existing.updated_at = now
        db.add(existing)
        db.flush()
        return existing

    record = Consent(
        id=new_id(),
        tenant_id=tenant_id,
        subject_user_id=subject_user_id,
        grantee_user_id=grantee_user_id,
        grantee_role=grantee_role,
        purpose=purpose,
        scopes=scopes,
        status="active",
        created_at=now,
        updated_at=now,
    )
    db.add(record)
    db.flush()
    return record


def withdraw_consent(
    db: Session,
    *,
    tenant_id: str,
    subject_user_id: str,
    purpose: str | None = None,
    grantee_user_id: str | None = None,
    consent_id: str | None = None,
) -> int:
    """Withdraw matching consents. Returns the number of records withdrawn."""
    stmt = select(Consent).where(
        Consent.tenant_id == tenant_id,
        Consent.subject_user_id == subject_user_id,
        Consent.status == "active",
    )
    if consent_id:
        stmt = stmt.where(Consent.id == consent_id)
    if purpose:
        stmt = stmt.where(Consent.purpose == purpose)
    if grantee_user_id:
        stmt = stmt.where(Consent.grantee_user_id == grantee_user_id)
    records = list(db.scalars(stmt).all())
    now = datetime.now(timezone.utc)
    for record in records:
        record.status = "withdrawn"
        record.updated_at = now
        db.add(record)
    db.flush()
    return len(records)


def shared_with(db: Session, tenant_id: str, subject_user_id: str) -> list[dict]:
    """Human-readable 'who has my data' view."""
    records = db.scalars(
        select(Consent).where(
            Consent.tenant_id == tenant_id,
            Consent.subject_user_id == subject_user_id,
        ).order_by(Consent.updated_at.desc())
    ).all()
    result = []
    for record in records:
        grantee_name = None
        if record.grantee_user_id:
            grantee = db.get(User, record.grantee_user_id)
            grantee_name = grantee.full_name if grantee else None
        result.append(
            {
                "consent_id": record.id,
                "grantee_user_id": record.grantee_user_id,
                "grantee_name": grantee_name,
                "grantee_role": record.grantee_role,
                "purpose": record.purpose,
                "scopes": record.scopes,
                "status": record.status,
                "updated_at": record.updated_at.isoformat() if record.updated_at else None,
            }
        )
    return result


def assert_access(
    db: Session,
    actor: User,
    subject_user_id: str,
    purpose: str,
    scope: str,
) -> None:
    """Convenience wrapper that also blocks access to withdrawn grants."""
    if not has_consent(db, actor, subject_user_id, purpose, scope):
        raise AppError(
            403,
            "consent_withdrawn_or_missing",
            "Access denied: consent is missing or was withdrawn.",
            {
                "subject_user_id": subject_user_id,
                "purpose": purpose,
                "scope": scope,
            },
        )
