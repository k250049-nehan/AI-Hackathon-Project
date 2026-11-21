"""Read-only audit views for officers, admins and auditors."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.audit import query_audit
from app.db import get_db
from app.schemas import AuditOut
from app.security import require_roles

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("", response_model=list[AuditOut], summary="Query the immutable audit trail")
def get_audit(
    actor_id: str | None = None,
    action: str | None = None,
    target_type: str | None = None,
    target_id: str | None = None,
    since: str | None = None,
    limit: int = Query(default=100, ge=1, le=1000),
    db: Session = Depends(get_db),
    actor=Depends(require_roles("auditor", "admin", "officer")),
) -> list[AuditOut]:
    parsed_since = None
    if since:
        try:
            parsed_since = datetime.fromisoformat(since.replace("Z", "+00:00"))
        except ValueError:
            parsed_since = None
    rows = query_audit(
        db,
        actor.tenant_id,
        actor_id=actor_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        since=parsed_since,
        limit=limit,
    )
    return [AuditOut.model_validate(row) for row in rows]


@router.get("/ai-decisions", summary="Every AI decision trace")
def ai_decisions(
    db: Session = Depends(get_db),
    actor=Depends(require_roles("auditor", "admin", "officer")),
) -> list[dict]:
    rows = query_audit(db, actor.tenant_id, action="ai.decision", limit=500)
    return [
        {
            "audit_id": row.id,
            "case_id": row.target_id,
            "created_at": row.created_at,
            "trace": row.detail,
        }
        for row in rows
    ]


@router.get("/consent-events", summary="Consent grants and withdrawals")
def consent_events(
    db: Session = Depends(get_db),
    actor=Depends(require_roles("auditor", "admin", "officer")),
) -> list[dict]:
    rows = [
        row
        for row in query_audit(db, actor.tenant_id, limit=1000)
        if row.action.startswith("consent.")
    ]
    return [
        {
            "audit_id": row.id,
            "action": row.action,
            "actor_id": row.actor_id,
            "detail": row.detail,
            "created_at": row.created_at,
        }
        for row in rows
    ]
