"""Rule publishing (no redeploy) and Digital Twin what-if simulation."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.audit import log
from app.db import get_db
from app.models import Case, RuleSet, User
from app.rules.engine import create_ruleset, evaluate_for_case, get_active_ruleset
from app.schemas import DigitalTwinRequest, RuleCreate, RuleOut
from app.security import get_current_user, require_roles

from app.api.helpers import actor_label

router = APIRouter(prefix="/api/rules", tags=["rules"])


@router.get("", response_model=list[RuleOut], summary="List all rule versions")
def list_rules(
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> list[RuleOut]:
    rows = db.scalars(
        select(RuleSet).where(RuleSet.tenant_id == actor.tenant_id).order_by(RuleSet.version.desc())
    ).all()
    return [RuleOut.model_validate(row) for row in rows]


@router.get("/active", response_model=RuleOut, summary="Currently active rule version")
def active_rule(
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> RuleOut:
    return RuleOut.model_validate(get_active_ruleset(db, actor.tenant_id))


@router.post("", response_model=RuleOut, status_code=201, summary="Publish a new rule version instantly")
def publish_rule(
    payload: RuleCreate,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles("admin")),
) -> RuleOut:
    definition = payload.definition.model_dump()
    ruleset = create_ruleset(
        db,
        tenant_id=actor.tenant_id,
        definition=definition,
        name=payload.name,
        change_note=payload.change_note,
        created_by=actor.id,
    )
    log(
        db,
        tenant_id=actor.tenant_id,
        actor_type="user",
        actor_id=actor.id,
        action="rule.published",
        target_type="rule_set",
        target_id=ruleset.id,
        detail={
            "version": ruleset.version,
            "change_note": payload.change_note,
            "definition": definition,
        },
    )
    db.commit()
    return RuleOut.model_validate(ruleset)


@router.post("/digital-twin/simulate", summary="Replay past cases against a proposed rule (no live change)")
def digital_twin(
    payload: DigitalTwinRequest,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles("admin", "auditor")),
) -> dict:
    if payload.case_ids:
        cases = [
            db.get(Case, case_id)
            for case_id in payload.case_ids
        ]
        cases = [case for case in cases if case and case.tenant_id == actor.tenant_id]
    else:
        cases = list(
            db.scalars(
                select(Case).where(Case.tenant_id == actor.tenant_id).order_by(Case.created_at.desc()).limit(200)
            ).all()
        )

    results = []
    for case in cases:
        trace = case.decision_trace or {}
        proposed = evaluate_for_case(
            db,
            case,
            definition_override=payload.definition.model_dump(),
            identity=trace.get("identity"),
            documents=None,
            jev=trace.get("jev"),
            anomaly=trace.get("anomaly"),
        )
        results.append(
            {
                "case_id": case.id,
                "case_number": case.case_number,
                "original_decision": case.decision,
                "proposed_decision": proposed["decision"],
                "changed": case.decision != proposed["decision"],
                "confidence": proposed["confidence"],
                "reasons": proposed["reasons"][:3],
            }
        )

    changed = sum(1 for item in results if item["changed"])
    log(
        db,
        tenant_id=actor.tenant_id,
        actor_type="user",
        actor_id=actor.id,
        action="rule.digital_twin_simulated",
        target_type="rule_set",
        target_id=None,
        detail={"cases_simulated": len(results), "decisions_changed": changed, "actor": actor_label(actor)},
    )
    db.commit()
    return {
        "cases_simulated": len(results),
        "decisions_changed": changed,
        "change_rate": round(changed / len(results), 4) if results else 0.0,
        "live_rules_unchanged": True,
        "results": results,
        "simulated": True,
    }
