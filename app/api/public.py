"""Public REST API. Authentication is an API key; scopes are enforced server-side."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.ai.jev import classify
from app.db import get_db
from app.errors import AppError
from app.models import ApiKey, Case, User
from app.rules.engine import get_active_ruleset
from app.schemas import CaseOut, PublicCaseCreate
from app.security import api_key_with_scope, enforce_consent, require_api_key

from app.api.helpers import enforce_usage_limit, load_case
from app.services.cases import create_case

router = APIRouter(prefix="/api/public", tags=["public-api"])


@router.get("/cases", response_model=list[CaseOut], summary="List cases (API key, cases:read)")
def public_list_cases(
    limit: int = 50,
    db: Session = Depends(get_db),
    payload: tuple[User, ApiKey] = Depends(api_key_with_scope("cases:read")),
) -> list[CaseOut]:
    user, _ = payload
    from sqlalchemy import select

    rows = db.scalars(
        select(Case).where(Case.tenant_id == user.tenant_id).order_by(Case.created_at.desc()).limit(limit)
    ).all()
    return [CaseOut.model_validate(row) for row in rows]


@router.post("/cases", response_model=CaseOut, status_code=201, summary="Create a case (API key, cases:write)")
def public_create_case(
    body: PublicCaseCreate,
    db: Session = Depends(get_db),
    payload: tuple[User, ApiKey] = Depends(api_key_with_scope("cases:write")),
) -> CaseOut:
    user, _ = payload
    subject = db.get(User, body.subject_user_id)
    if not subject or subject.tenant_id != user.tenant_id:
        raise AppError(404, "not_found", "Subject user not found in your workspace.")
    if subject.id != user.id:
        enforce_consent(db, user, subject.id, "relief_claim_assist", "submit_claim")
    enforce_usage_limit(db, user.tenant_id)
    case = create_case(
        db,
        tenant_id=user.tenant_id,
        subject_user_id=subject.id,
        created_by=user.id,
        case_type=body.case_type,
        raw_text=body.raw_text,
        intake_channel="text",
        district=body.district,
    )
    db.commit()
    return CaseOut.model_validate(case)


@router.get("/cases/{case_id}", response_model=CaseOut, summary="Read one case (API key, cases:read)")
def public_get_case(
    case_id: str,
    db: Session = Depends(get_db),
    payload: tuple[User, ApiKey] = Depends(api_key_with_scope("cases:read")),
) -> CaseOut:
    user, _ = payload
    return CaseOut.model_validate(load_case(db, case_id, user))


@router.post("/classify", summary="Classify a message (API key, ai:infer)")
def public_classify(
    body: dict,
    db: Session = Depends(get_db),
    payload: tuple[User, ApiKey] = Depends(api_key_with_scope("ai:infer")),
) -> dict:
    user, _ = payload
    ruleset = get_active_ruleset(db, user.tenant_id)
    result = classify(
        str(body.get("text", "")),
        {
            "auto_approve_min_confidence": ruleset.definition["auto_approve_min_confidence"],
            "ask_info_min_confidence": ruleset.definition["ask_info_min_confidence"],
            "scam_block_confidence": ruleset.definition["scam_block_confidence"],
        },
    )
    return result


@router.get("/whoami", summary="Identify the API key owner")
def whoami(payload: tuple[User, ApiKey] = Depends(require_api_key)) -> dict:
    user, key = payload
    return {
        "user_id": user.id,
        "tenant_id": user.tenant_id,
        "role": user.role,
        "key_name": key.name,
        "scopes": key.scopes,
    }
