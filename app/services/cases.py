"""Case creation pipeline shared by every entry point."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.ai import anomaly as anomaly_module
from app.ai import jev as jev_module
from app.ai.explain import explain
from app.audit import log
from app.models import Case, Tenant, new_id
from app.rules.engine import evaluate, get_active_ruleset
from app.services import mock_identity, notifications, webhooks

STATUS_BY_DECISION = {
    "approve": "pending_officer",
    "needs_info": "needs_info",
    "human_review": "human_review",
    "block": "blocked",
}


def next_case_number(db: Session, tenant_id: str) -> str:
    tenant = db.get(Tenant, tenant_id)
    prefix = (tenant.slug[:4] if tenant else "case").upper()
    count = db.query(Case).filter(Case.tenant_id == tenant_id).count() + 1
    return f"RC-{prefix}-{count:05d}"


def create_case(
    db: Session,
    *,
    tenant_id: str,
    subject_user_id: str,
    created_by: str,
    case_type: str = "relief_claim",
    raw_text: str | None = None,
    claim_data: dict | None = None,
    intake_channel: str = "text",
    district: str | None = None,
    assigned_to: str | None = None,
    priority: str | None = None,
) -> Case:
    """Create a case and run classification, rules and explainability inline."""
    active = get_active_ruleset(db, tenant_id)
    definition = active.definition
    claim = claim_data or {}
    text = raw_text or ""
    thresholds = {
        "auto_approve_min_confidence": definition["auto_approve_min_confidence"],
        "ask_info_min_confidence": definition["ask_info_min_confidence"],
        "scam_block_confidence": definition["scam_block_confidence"],
    }

    jev_result = jev_module.classify(text or "relief claim", thresholds)
    identity = mock_identity.verify(claim.get("cnic"), claim.get("full_name"))
    past = [
        row.claim_data or {}
        for row in db.query(Case)
        .filter(Case.tenant_id == tenant_id, Case.case_type == "relief_claim")
        .limit(50)
        .all()
    ]
    anomaly_result = anomaly_module.detect_anomaly(
        claim,
        past,
        definition["duplicate_window_days"],
        definition["max_duplicate_claims"],
    )

    rule_result = evaluate(
        definition=definition,
        claim=claim,
        identity=identity,
        documents=None,
        jev=jev_result,
        anomaly=anomaly_result,
    )
    rule_result["rule_version"] = active.version
    rule_result["rule_set_id"] = active.id

    decision = rule_result["decision"]
    explanation = explain(
        decision,
        rule_result["reasons"],
        {"checks": rule_result["checks"], "jev": jev_result, "identity": identity, "anomaly": anomaly_result},
        rule_result["confidence"],
        subject_user_id=subject_user_id,
        rule_version=active.version,
        model_versions={
            "rules": f"rule-set-v{active.version}",
            "jev": jev_result["model_version"],
            "anomaly": anomaly_result["model_version"],
        },
        input_data={"claim": claim, "text": text[:500]},
    )

    case = Case(
        id=new_id(),
        tenant_id=tenant_id,
        case_number=next_case_number(db, tenant_id),
        case_type=case_type,
        subject_user_id=subject_user_id,
        created_by=created_by,
        assigned_to=assigned_to,
        status=STATUS_BY_DECISION.get(decision, "human_review"),
        priority=priority or ("high" if decision == "block" or anomaly_result["flagged"] else "normal"),
        confidence=rule_result["confidence"],
        jev_label=jev_result["label"],
        jev_scores=jev_result["scores"],
        decision=decision,
        decision_reason_simple=explanation["simple"],
        decision_trace={
            **rule_result,
            "explanation": explanation,
            "jev": jev_result,
            "identity": identity,
            "anomaly": anomaly_result,
        },
        rule_set_id=active.id,
        raw_text=text[:4000] or None,
        district=district or claim.get("district"),
        claim_data=claim,
        risk_flag="anomaly" if anomaly_result["flagged"] else None,
        intake_channel=intake_channel,
    )
    db.add(case)
    db.flush()

    log(
        db,
        tenant_id=tenant_id,
        actor_type="user",
        actor_id=created_by,
        action="case.created",
        target_type="case",
        target_id=case.id,
        detail={
            "case_number": case.case_number,
            "case_type": case_type,
            "intake_channel": intake_channel,
            "simulated": True,
        },
    )
    log(
        db,
        tenant_id=tenant_id,
        actor_type="ai",
        actor_id=jev_result["model_version"],
        action="ai.decision",
        target_type="case",
        target_id=case.id,
        detail=explanation["audit_trace"],
    )
    notifications.notify(
        db,
        tenant_id=tenant_id,
        user_id=subject_user_id,
        title="Case created / درخواست موصول",
        body=f"Your case {case.case_number} was received. Status: {case.status}.",
        actor_id=created_by,
    )
    webhooks.dispatch(
        db,
        tenant_id=tenant_id,
        event="case.created",
        payload={"case_id": case.id, "case_number": case.case_number, "status": case.status, "mock": True},
    )
    db.flush()
    return case
