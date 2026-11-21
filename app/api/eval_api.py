"""Evaluation dashboard: accuracy, false alarms, speed and cost."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.audit import log
from app.db import get_db
from app.models import EvaluationRecord, User
from app.schemas import EvaluationRecordIn
from app.security import get_current_user, require_roles
from app.services.evaluation import record_evaluation, summary

router = APIRouter(prefix="/api/evaluation", tags=["evaluation"])


@router.get("/summary", summary="Evaluation metrics and cost trade-off")
def evaluation_summary(
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> dict:
    return summary(db, actor.tenant_id)


@router.get("/records", summary="Raw evaluation records")
def evaluation_records(
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> list[dict]:
    rows = db.scalars(
        select(EvaluationRecord).where(EvaluationRecord.tenant_id == actor.tenant_id).order_by(
            EvaluationRecord.created_at.desc()
        ).limit(500)
    ).all()
    return [
        {
            "id": row.id,
            "case_id": row.case_id,
            "predicted_label": row.predicted_label,
            "actual_label": row.actual_label,
            "confidence": row.confidence,
            "latency_ms": row.latency_ms,
            "false_alarm": row.was_false_alarm,
            "missed": row.was_missed,
            "created_at": row.created_at,
        }
        for row in rows
    ]


@router.post("/records", status_code=201, summary="Add a human-labelled evaluation sample")
def add_evaluation_record(
    payload: EvaluationRecordIn,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles("officer", "admin")),
) -> dict:
    record = record_evaluation(
        db,
        tenant_id=actor.tenant_id,
        case_id=payload.case_id,
        predicted_label=payload.predicted_label,
        actual_label=payload.actual_label,
        confidence=payload.confidence,
        latency_ms=payload.latency_ms,
        notes=payload.notes,
    )
    log(
        db,
        tenant_id=actor.tenant_id,
        actor_type="user",
        actor_id=actor.id,
        action="evaluation.recorded",
        target_type="evaluation_record",
        target_id=record.id,
        detail={"predicted": payload.predicted_label, "actual": payload.actual_label},
    )
    db.commit()
    return {
        "id": record.id,
        "false_alarm": record.was_false_alarm,
        "missed": record.was_missed,
    }
