"""Consent visibility, sharing, correction and true withdrawal."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.audit import log
from app.consent import grant_consent, shared_with, withdraw_consent
from app.db import get_db
from app.errors import AppError
from app.models import User
from app.schemas import ConsentCreate, ConsentOut
from app.security import get_current_user, has_consent, require_roles

from app.api.helpers import actor_label

router = APIRouter(prefix="/api/consent", tags=["consent"])


@router.get("/mine", summary="See who has my data")
def my_consents(
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> dict:
    return {
        "subject_user_id": actor.id,
        "shared_with": shared_with(db, actor.tenant_id, actor.id),
        "simulated": True,
    }


@router.get("/subject/{subject_user_id}", response_model=list[ConsentOut], summary="Consent records for a subject")
def subject_consents(
    subject_user_id: str,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles("helper", "officer", "admin", "auditor")),
) -> list[ConsentOut]:
    subject = db.get(User, subject_user_id)
    if not subject or subject.tenant_id != actor.tenant_id:
        raise AppError(404, "not_found", "Subject user not found.")
    rows = shared_with(db, actor.tenant_id, subject_user_id)
    return [
        ConsentOut(
            id=row["consent_id"],
            tenant_id=actor.tenant_id,
            subject_user_id=subject_user_id,
            grantee_user_id=row["grantee_user_id"],
            grantee_role=row["grantee_role"],
            purpose=row["purpose"],
            scopes=row["scopes"],
            status=row["status"],
            updated_at=row["updated_at"],
        )
        for row in rows
        if row["status"] != "withdrawn" or actor.role in {"admin", "auditor"}
    ]


@router.post("/grant", response_model=ConsentOut, status_code=201, summary="Grant or restore consent")
def grant(
    payload: ConsentCreate,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> ConsentOut:
    if payload.subject_user_id != actor.id and actor.role not in {"admin", "helper"}:
        raise AppError(403, "role_denied", "Only the subject, a helper or an admin can grant consent.")
    subject = db.get(User, payload.subject_user_id)
    if not subject or subject.tenant_id != actor.tenant_id:
        raise AppError(404, "not_found", "Subject user not found.")
    if payload.subject_user_id != actor.id and not has_consent(
        db, actor, payload.subject_user_id, "relief_claim_assist", "manage_consent"
    ):
        raise AppError(403, "consent_required", "No consent to manage this person's data.")

    record = grant_consent(
        db,
        tenant_id=actor.tenant_id,
        subject_user_id=payload.subject_user_id,
        purpose=payload.purpose,
        scopes=payload.scopes,
        grantee_user_id=payload.grantee_user_id,
        grantee_role=payload.grantee_role,
    )
    log(
        db,
        tenant_id=actor.tenant_id,
        actor_type="user",
        actor_id=actor.id,
        action="consent.granted",
        target_type="consent",
        target_id=record.id,
        detail={
            "subject_user_id": payload.subject_user_id,
            "purpose": payload.purpose,
            "scopes": payload.scopes,
            "actor": actor_label(actor),
        },
    )
    db.commit()
    return ConsentOut.model_validate(record)


@router.post("/withdraw", summary="Withdraw consent (access stops immediately)")
def withdraw(
    payload: ConsentCreate,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> dict:
    if payload.subject_user_id != actor.id and actor.role != "admin":
        raise AppError(403, "role_denied", "Only the subject or an admin can withdraw consent.")
    count = withdraw_consent(
        db,
        tenant_id=actor.tenant_id,
        subject_user_id=payload.subject_user_id,
        purpose=payload.purpose,
        grantee_user_id=payload.grantee_user_id,
    )
    log(
        db,
        tenant_id=actor.tenant_id,
        actor_type="user",
        actor_id=actor.id,
        action="consent.withdrawn",
        target_type="consent",
        target_id=payload.grantee_user_id,
        detail={
            "subject_user_id": payload.subject_user_id,
            "purpose": payload.purpose,
            "grantee_user_id": payload.grantee_user_id,
            "records_withdrawn": count,
            "access_blocked": True,
            "effect": "All matching access is denied on the next server-side check.",
            "actor": actor_label(actor),
        },
    )
    db.commit()
    return {
        "withdrawn_records": count,
        "access_blocked": True,
        "audit_logged": True,
        "simulated": True,
    }


@router.post("/correct", summary="Correct your own mock profile data")
def correct_data(
    payload: dict,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> dict:
    allowed = {"full_name", "phone", "preferred_language"}
    updates = {key: str(value)[:200] for key, value in (payload or {}).items() if key in allowed}
    if not updates:
        raise AppError(422, "no_valid_fields", "Provide at least one of: full_name, phone, preferred_language.")
    before = {key: getattr(actor, key) for key in updates}
    for key, value in updates.items():
        setattr(actor, key, value)
    log(
        db,
        tenant_id=actor.tenant_id,
        actor_type="user",
        actor_id=actor.id,
        action="consent.data_corrected",
        target_type="user",
        target_id=actor.id,
        detail={"before": before, "after": updates, "actor": actor_label(actor)},
    )
    db.commit()
    return {"corrected": updates, "audit_logged": True}


@router.get("/check", summary="Check an access decision (server-side truth)")
def check_access(
    subject_user_id: str,
    purpose: str,
    scope: str,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> dict:
    allowed = has_consent(db, actor, subject_user_id, purpose, scope)
    return {
        "actor_id": actor.id,
        "actor_role": actor.role,
        "subject_user_id": subject_user_id,
        "purpose": purpose,
        "scope": scope,
        "allowed": allowed,
        "simulated": True,
    }
