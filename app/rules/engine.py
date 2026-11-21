"""Rule evaluation with versioning and a cost-aware action threshold.

An admin can publish a new rule version through the API. New cases immediately
use the active version; old cases keep the `rule_set_id` used at decision time,
so an auditor can always reconstruct the past decision.
"""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.errors import AppError
from app.models import Case, RuleSet, new_id
from app.schemas import RuleDefinition

DEFAULT_DEFINITION = RuleDefinition().model_dump()

THRESHOLDS = {
    "auto_approve_min_confidence": 0.90,
    "ask_info_min_confidence": 0.65,
    "scam_block_confidence": 0.85,
}


def get_active_ruleset(db: Session, tenant_id: str, *, name: str = "relief_eligibility") -> RuleSet:
    ruleset = db.scalar(
        select(RuleSet).where(
            RuleSet.tenant_id == tenant_id,
            RuleSet.name == name,
            RuleSet.is_active.is_(True),
        ).order_by(RuleSet.version.desc())
    )
    if not ruleset:
        raise AppError(404, "no_active_ruleset", "No active rule set is configured for this workspace.")
    return ruleset


def create_ruleset(
    db: Session,
    *,
    tenant_id: str,
    definition: dict,
    name: str = "relief_eligibility",
    change_note: str = "",
    created_by: str | None = None,
) -> RuleSet:
    """Publish a new immutable rule version and deactivate the previous one."""
    next_version = int(
        db.scalar(
            select(func.coalesce(func.max(RuleSet.version), 0)).where(
                RuleSet.tenant_id == tenant_id, RuleSet.name == name
            )
        )
        or 0
    ) + 1
    existing = db.scalars(
        select(RuleSet).where(RuleSet.tenant_id == tenant_id, RuleSet.name == name, RuleSet.is_active.is_(True))
    ).all()
    for record in existing:
        record.is_active = False
        db.add(record)

    ruleset = RuleSet(
        id=new_id(),
        tenant_id=tenant_id,
        name=name,
        version=next_version,
        definition=dict(definition),
        is_active=True,
        created_by=created_by,
        change_note=change_note,
    )
    db.add(ruleset)
    db.flush()
    return ruleset


def _document_types(documents: list[dict] | None, claim: dict) -> set[str]:
    types = {
        str(item.get("doc_type", "")).lower()
        for item in (documents or [])
        if isinstance(item, dict) and item.get("doc_type")
    }
    # A structured claim that contains a CNIC counts as providing the CNIC field.
    if claim.get("cnic"):
        types.add("cnic")
    if claim.get("income_certificate"):
        types.add("income_certificate")
    return types


def evaluate(
    *,
    definition: dict,
    claim: dict | None = None,
    identity: dict | None = None,
    documents: list[dict] | None = None,
    jev: dict | None = None,
    anomaly: dict | None = None,
) -> dict:
    """Evaluate a claim against one immutable rule definition (pure function)."""
    claim = claim or {}
    identity = identity or {}
    jev = jev or {}
    anomaly = anomaly or {}
    definition = {**DEFAULT_DEFINITION, **definition}

    checks: list[dict] = []

    def add(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    cnic_present = bool(claim.get("cnic"))
    add("cnic_present", cnic_present, "CNIC number is present on the claim.")

    verified = bool(identity.get("verified"))
    add(
        "identity_verified",
        verified,
        "Mock identity service confirmed the record." if verified else "Identity is not verified yet.",
    )

    if not cnic_present:
        add("name_present", False, "Applicant name is missing.")
    else:
        add("name_present", bool(claim.get("full_name")), "Applicant name is present.")

    income = claim.get("monthly_income")
    income_ok = isinstance(income, (int, float)) and (
        definition["min_income"] <= income <= definition["max_income"]
    )
    add(
        "income_in_range",
        income_ok,
        f"Declared income {income} against allowed range "
        f"{definition['min_income']}-{definition['max_income']}.",
    )

    category_ok = claim.get("category") in definition["allowed_categories"]
    add("category_allowed", category_ok, f"Category '{claim.get('category')}' checked.")

    amount = claim.get("claim_amount")
    amount_ok = isinstance(amount, (int, float)) and 0 < amount <= definition["max_claim_amount"]
    add(
        "amount_within_limit",
        amount_ok,
        f"Claim amount {amount} against limit {definition['max_claim_amount']}.",
    )

    available_docs = _document_types(documents, claim)
    missing_docs = [doc for doc in definition["required_documents"] if doc not in available_docs]
    add("documents_present", not missing_docs, f"Missing documents: {missing_docs or 'none'}.")

    add(
        "no_anomaly",
        not anomaly.get("flagged"),
        anomaly.get("reasons") or "No suspicious pattern detected.",
    )

    scam_label = jev.get("label") == "scam"
    add(
        "not_scam",
        not scam_label,
        "Message was classified as a scam." if scam_label else "No scam signals detected.",
    )

    identity_confidence = float(identity.get("confidence") or 0.0)
    jev_confidence = float(jev.get("confidence") or 0.0)
    confidence = round(
        max(0.0, min(1.0, 0.45 * jev_confidence + 0.55 * identity_confidence - 0.3 * float(anomaly.get("score") or 0.0))),
        4,
    )

    failed = [check["name"] for check in checks if not check["passed"]]
    reasons = [f"{check['name']}: {check['detail']}" for check in checks if not check["passed"]]

    auto_threshold = float(definition["auto_approve_min_confidence"])
    ask_threshold = float(definition["ask_info_min_confidence"])
    scam_threshold = float(definition["scam_block_confidence"])

    if scam_label and jev_confidence >= scam_threshold:
        decision, route = "block", "auto_block"
        reasons.insert(0, "Scam classification confidence exceeds the block threshold.")
    elif confidence < ask_threshold:
        decision, route = "human_review", "human_handoff"
        reasons.insert(0, f"Confidence {confidence:.2f} is below {ask_threshold:.2f}.")
    elif "identity_verified" in failed or "cnic_present" in failed or "name_present" in failed:
        decision, route = "needs_info", "ask_more_info"
    elif failed:
        decision, route = "human_review", "human_handoff"
        reasons.insert(0, "One or more eligibility checks failed; a human decides.")
    elif confidence >= auto_threshold:
        decision, route = "approve", "auto_handle"
    else:
        decision, route = "needs_info", "ask_more_info"

    return {
        "decision": decision,
        "route": route,
        "confidence": confidence,
        "checks": checks,
        "failed_checks": failed,
        "reasons": reasons or ["All rule checks passed."],
        "thresholds": {
            "auto_approve_min_confidence": auto_threshold,
            "ask_info_min_confidence": ask_threshold,
            "scam_block_confidence": scam_threshold,
        },
        "cost_model": {
            "false_approve": 100.0,
            "false_reject": 10.0,
            "manual_review": 1.0,
            "policy": "A wrong approval costs 10x a wrong rejection, so uncertain cases are never auto-approved.",
        },
    }


def evaluate_for_case(
    db: Session,
    case: Case,
    *,
    ruleset: RuleSet | None = None,
    definition_override: dict | None = None,
    identity: dict | None = None,
    documents: list[dict] | None = None,
    jev: dict | None = None,
    anomaly: dict | None = None,
) -> dict:
    """Evaluate a persisted case using its rule version (or an override)."""
    if definition_override is not None:
        ruleset_used = ruleset
        definition = {**DEFAULT_DEFINITION, **definition_override}
    else:
        ruleset_used = ruleset or (
            db.get(RuleSet, case.rule_set_id) if case.rule_set_id else get_active_ruleset(db, case.tenant_id)
        )
        definition = ruleset_used.definition
    result = evaluate(
        definition=definition,
        claim=case.claim_data or {},
        identity=identity,
        documents=documents,
        jev=jev,
        anomaly=anomaly,
    )
    result["rule_set_id"] = ruleset_used.id if ruleset_used else None
    result["rule_version"] = ruleset_used.version if ruleset_used else None
    return result
