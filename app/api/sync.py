"""Offline-first sync: queued client operations replayed exactly once."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.structured import prepare_voice_claim
from app.db import get_db
from app.errors import AppError
from app.models import SyncOperation, User
from app.schemas import SyncRequest, SyncResult
from app.security import enforce_consent, get_current_user

from app.api.helpers import enforce_usage_limit
from app.services.cases import create_case

router = APIRouter(prefix="/api/sync", tags=["offline"])


def _process(db: Session, actor: User, op_type: str, payload: dict) -> dict:
    subject = payload.get("subject_user_id") or actor.id
    if subject != actor.id:
        enforce_consent(db, actor, str(subject), "relief_claim_assist", "submit_claim")
    enforce_usage_limit(db, actor.tenant_id)

    channel = "offline"
    raw_text = str(payload.get("raw_text") or payload.get("transcript") or "")[:4000]
    claim_data: dict = {}
    if op_type == "voice_intake":
        channel = "voice"
        prepared = prepare_voice_claim(raw_text, payload.get("claim_data"))
        if prepared["errors"]:
            raise AppError(
                422,
                "invalid_claim",
                "Structured claim failed validation.",
                {"errors": prepared["errors"]},
            )
        claim_data = dict(prepared["claim"])
    elif op_type == "scam_report":
        channel = payload.get("intake_channel", "offline")

    case = create_case(
        db,
        tenant_id=actor.tenant_id,
        subject_user_id=str(subject),
        created_by=actor.id,
        case_type=str(payload.get("case_type", "scam_report" if op_type == "scam_report" else "relief_claim")),
        raw_text=raw_text,
        claim_data=claim_data,
        intake_channel=channel,
        district=payload.get("district"),
    )
    db.flush()
    return {
        "case_id": case.id,
        "case_number": case.case_number,
        "status": case.status,
        "decision": case.decision,
    }


@router.post("", response_model=SyncResult, summary="Replay offline operations idempotently")
def sync_operations(
    payload: SyncRequest,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> SyncResult:
    results: list[dict] = []
    duplicates = 0
    for operation in payload.operations:
        existing = db.scalar(
            select(SyncOperation).where(
                SyncOperation.client_id == payload.client_id,
                SyncOperation.op_id == operation.op_id,
            )
        )
        if existing:
            duplicates += 1
            results.append({"op_id": operation.op_id, "duplicate": True, "result": existing.result})
            continue
        try:
            result = _process(db, actor, operation.op_type, operation.payload)
        except AppError as exc:
            result = {"op_id": operation.op_id, "error": exc.code, "message": exc.message}
        record = SyncOperation(
            tenant_id=actor.tenant_id,
            client_id=payload.client_id,
            op_id=operation.op_id,
            op_type=operation.op_type,
            payload=operation.payload,
            result=result,
        )
        db.add(record)
        db.flush()
        results.append({"op_id": operation.op_id, "duplicate": False, "result": result})
    db.commit()
    return SyncResult(
        client_id=payload.client_id,
        processed=len(payload.operations) - duplicates,
        duplicates_skipped=duplicates,
        results=results,
    )


@router.get("/status", summary="Inspect previously synced operations")
def sync_status(
    client_id: str,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> dict:
    rows = db.scalars(
        select(SyncOperation).where(
            SyncOperation.tenant_id == actor.tenant_id,
            SyncOperation.client_id == client_id,
        )
    ).all()
    return {
        "client_id": client_id,
        "operations": [{"op_id": row.op_id, "op_type": row.op_type, "result": row.result} for row in rows],
    }
