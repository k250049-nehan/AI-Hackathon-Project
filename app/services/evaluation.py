"""Evaluation dashboard metrics and the published cost trade-off numbers."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import EvaluationRecord


def record_evaluation(
    db: Session,
    *,
    tenant_id: str,
    case_id: str | None,
    predicted_label: str,
    actual_label: str,
    confidence: float,
    latency_ms: float,
    notes: str | None = None,
) -> EvaluationRecord:
    predicted_scam = predicted_label == "scam"
    actual_scam = actual_label == "scam"
    record = EvaluationRecord(
        tenant_id=tenant_id,
        case_id=case_id,
        predicted_label=predicted_label,
        actual_label=actual_label,
        confidence=round(float(confidence), 4),
        latency_ms=round(float(latency_ms), 3),
        was_false_alarm=bool(predicted_scam and not actual_scam),
        was_missed=bool(actual_scam and not predicted_scam),
        notes=notes,
    )
    db.add(record)
    db.flush()
    return record


def summary(db: Session, tenant_id: str) -> dict:
    rows = list(
        db.scalars(
            select(EvaluationRecord).where(EvaluationRecord.tenant_id == tenant_id)
        ).all()
    )
    total = len(rows)
    correct = sum(1 for row in rows if row.predicted_label == row.actual_label)
    true_positive = sum(
        1 for row in rows if row.predicted_label == "scam" and row.actual_label == "scam"
    )
    false_positive = sum(1 for row in rows if row.was_false_alarm)
    false_negative = sum(1 for row in rows if row.was_missed)
    precision = true_positive / (true_positive + false_positive) if (true_positive + false_positive) else 1.0
    recall = true_positive / (true_positive + false_negative) if (true_positive + false_negative) else 1.0

    cost = (
        false_positive * settings.cost_false_approve
        + false_negative * settings.cost_false_reject
        + max(0, total - true_positive - false_positive - false_negative) * settings.cost_manual_review
    )
    return {
        "total_evaluations": total,
        "accuracy": round(correct / total, 4) if total else 1.0,
        "precision_scam": round(precision, 4),
        "recall_scam": round(recall, 4),
        "false_alarms": false_positive,
        "false_alarm_rate": round(false_positive / total, 4) if total else 0.0,
        "missed_scams": false_negative,
        "avg_confidence": round(sum(row.confidence for row in rows) / total, 4) if total else 0.0,
        "avg_latency_ms": round(sum(row.latency_ms for row in rows) / total, 3) if total else 0.0,
        "estimated_cost_units": round(cost, 2),
        "cost_model": {
            "wrong_approval": settings.cost_false_approve,
            "wrong_rejection": settings.cost_false_reject,
            "manual_review": settings.cost_manual_review,
            "ratio": settings.cost_false_approve / settings.cost_false_reject,
            "explanation": (
                "A wrong approval costs 10x a wrong rejection, so the system never "
                "auto-releases payment and hands uncertain cases to a human."
            ),
        },
        "thresholds": {
            "auto_approve": settings.auto_approve_min_confidence,
            "ask_more_info": settings.ask_info_min_confidence,
            "scam_block": settings.scam_block_confidence,
        },
        "live_thresholds": _active_thresholds(db, tenant_id),
        "simulated": True,
    }


def _active_thresholds(db: Session, tenant_id: str) -> dict:
    from app.rules.engine import get_active_ruleset

    try:
        ruleset = get_active_ruleset(db, tenant_id)
    except Exception:
        return {}
    definition = ruleset.definition or {}
    return {
        "rule_version": ruleset.version,
        "auto_approve": definition.get("auto_approve_min_confidence"),
        "ask_more_info": definition.get("ask_info_min_confidence"),
        "scam_block": definition.get("scam_block_confidence"),
    }
