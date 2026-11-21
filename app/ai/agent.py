"""Autonomous agent with tool calling and a mandatory human-approval gate."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai import anomaly as anomaly_module
from app.ai import jev as jev_module
from app.ai.guardrails import requires_human_approval
from app.audit import log
from app.models import Case, User
from app.rules.engine import evaluate_for_case, get_active_ruleset
from app.services import mock_data, mock_identity, mock_payment

PLAN = [
    "Classify the incoming message and score confidence",
    "Verify identity through the mock identity service",
    "Fetch the consented mock data record",
    "Check for duplicate or anomalous claims",
    "Evaluate the active eligibility rule version",
    "Apply guardrails and request human approval for risky steps",
]


def _past_claims(db: Session, case: Case) -> list[dict]:
    rows = db.scalars(
        select(Case).where(
            Case.tenant_id == case.tenant_id,
            Case.case_type == "relief_claim",
            Case.id != case.id,
        ).limit(50)
    ).all()
    return [row.claim_data or {} for row in rows]


def run_agent(db: Session, case: Case, actor: User) -> dict:
    """Run the relief-claim workflow. All tool calls are recorded in the audit log."""
    steps: list[dict] = []

    def record(step: str, tool: str, payload: dict, output: dict) -> None:
        steps.append({"step": step, "tool": tool, "input": payload, "output": output, "mock": True})
        log(
            db,
            tenant_id=case.tenant_id,
            actor_type="agent",
            actor_id=actor.id,
            action=f"agent.tool.{tool}",
            target_type="case",
            target_id=case.id,
            detail={"step": step, "input": payload, "output": output, "simulated": True},
        )

    active = get_active_ruleset(db, case.tenant_id)
    definition = active.definition
    claim = case.claim_data or {}

    jev_result = jev_module.classify(
        case.raw_text or "relief claim",
        {
            "auto_approve_min_confidence": definition["auto_approve_min_confidence"],
            "ask_info_min_confidence": definition["ask_info_min_confidence"],
            "scam_block_confidence": definition["scam_block_confidence"],
        },
    )
    record("Classify message", "jev.classify", {"text": (case.raw_text or "")[:300]}, jev_result)

    identity = mock_identity.verify(claim.get("cnic"), claim.get("full_name"))
    record("Verify identity", "mock_identity.verify", {"cnic": claim.get("cnic")}, identity)

    data_record = mock_data.get_record(claim.get("cnic"))
    record("Fetch data record", "mock_data.get_record", {"cnic": claim.get("cnic")}, data_record)

    anomaly_result = anomaly_module.detect_anomaly(
        claim,
        _past_claims(db, case),
        definition["duplicate_window_days"],
        definition["max_duplicate_claims"],
    )
    record("Check anomalies", "anomaly.detect", {"cnic": claim.get("cnic")}, anomaly_result)

    rule_result = evaluate_for_case(
        db,
        case,
        ruleset=active,
        identity=identity,
        documents=None,
        jev=jev_result,
        anomaly=anomaly_result,
    )
    record(
        "Evaluate rules",
        "rules.evaluate",
        {"rule_version": active.version},
        {
            "decision": rule_result["decision"],
            "confidence": rule_result["confidence"],
            "failed_checks": rule_result["failed_checks"],
        },
    )

    approval_required, approval_reason = requires_human_approval(
        "disburse_payment", rule_result["confidence"], definition
    )
    payment = None
    if rule_result["decision"] == "approve" and not approval_required:
        payment = mock_payment.disburse(case.case_number, claim.get("claim_amount", 0), approved_by="auto")
    record(
        "Apply guardrails",
        "guardrails.check",
        {"decision": rule_result["decision"]},
        {
            "human_approval_required": approval_required,
            "reason": approval_reason,
            "payment": payment,
        },
    )

    db.flush()
    return {
        "case_id": case.id,
        "plan": PLAN,
        "steps": steps,
        "final_decision": rule_result["decision"],
        "human_approval_required": approval_required,
        "rule_version": active.version,
        "simulated": True,
    }
