"""Two-view explainability: plain language for citizens, full trace for auditors."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

from app.ai.guardrails import redact_pii

SIMPLE_MESSAGES = {
    "approved": "We approved your Relief Payment claim. {why}",
    "rejected": "We could not approve this claim. {why}",
    "needs_info": "We need a little more information before we decide. {why}",
    "human_review": "We are not sure, so a human officer will check your case. {why}",
    "auto_block": "We stopped this message because it looks like a scam. {why}",
    "escalated": "Your case was sent to a senior officer. {why}",
}

URDU_MESSAGES = {
    "approved": "آپ کی رلیف ادائیگی کی درخواست منظور ہو گئی۔ {why}",
    "rejected": "اس درخواست کو منظور نہیں کیا جا سکا۔ {why}",
    "needs_info": "فیصلے سے پہلے ہمیں تھوڑی مزید معلومات چاہیے۔ {why}",
    "human_review": "ہمیں یقین نہیں ہے، اس لیے ایک انسانی افسر آپ کی درخواست دیکھے گا۔ {why}",
    "auto_block": "یہ پیغام جعلی لگتا ہے اس لیے ہم نے اسے روک دیا۔ {why}",
    "escalated": "آپ کی درخواست سینئر افسر کو بھیج دی گئی۔ {why}",
}


def _hash_input(value: object) -> str:
    serialized = json.dumps(value, sort_keys=True, default=str, ensure_ascii=False)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:16]


def _plain_reason(reason: str) -> str:
    """Keep the human sentence, drop the internal rule id from citizen copy."""
    head, sep, tail = reason.partition(": ")
    if sep and head and " " not in head and len(head) <= 40:
        return tail.strip()
    return reason


def explain(
    decision: str,
    reasons: list[str] | None,
    trace: dict | None,
    confidence: float,
    *,
    subject_user_id: str | None = None,
    rule_version: int | None = None,
    model_versions: dict | None = None,
    input_data: object = None,
) -> dict:
    """Produce both the citizen view and the auditor view of one decision."""
    reasons = [redact_pii(str(reason)) for reason in (reasons or [])]
    why = " ".join(_plain_reason(reason) for reason in reasons[:2])
    template = SIMPLE_MESSAGES.get(decision, "A decision was recorded. {why}")
    urdu_template = URDU_MESSAGES.get(decision, "ایک فیصلہ درج کیا گیا۔ {why}")

    audit_trace = {
        "decision": decision,
        "result": decision,
        "confidence": round(float(confidence), 4),
        "reasons": reasons,
        "rule_version": rule_version,
        "model_versions": model_versions or {},
        "subject_user_id": subject_user_id,
        "input_hash": _hash_input(input_data if input_data is not None else trace or {}),
        "trace": trace or {},
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "simulated": True,
    }
    return {
        "simple": template.format(why=why).strip(),
        "simple_urdu": urdu_template.format(why=why).strip(),
        "audit_trace": audit_trace,
    }
