"""Immutable-style audit trail for every user, AI and agent action."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AuditLog, new_id


def log(
    db: Session,
    *,
    tenant_id: str,
    actor_type: str,
    actor_id: str,
    action: str,
    target_type: str | None = None,
    target_id: str | None = None,
    detail: dict[str, Any] | None = None,
) -> AuditLog:
    """Append an audit entry to the current transaction."""
    entry = AuditLog(
        id=new_id(),
        tenant_id=tenant_id,
        actor_type=actor_type,
        actor_id=str(actor_id),
        action=action,
        target_type=target_type,
        target_id=str(target_id) if target_id is not None else None,
        detail=detail or {},
        created_at=datetime.now(timezone.utc),
    )
    db.add(entry)
    db.flush()
    return entry


def log_standalone(
    *,
    tenant_id: str,
    actor_type: str,
    actor_id: str,
    action: str,
    target_type: str | None = None,
    target_id: str | None = None,
    detail: dict[str, Any] | None = None,
) -> None:
    """Write an audit entry in its own committed transaction.

    Used for security failures where the main request transaction may roll back.
    """
    import app.db as db_module

    with db_module.session_scope() as session:
        log(
            session,
            tenant_id=tenant_id,
            actor_type=actor_type,
            actor_id=actor_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            detail=detail,
        )


def query_audit(
    db: Session,
    tenant_id: str,
    *,
    actor_id: str | None = None,
    action: str | None = None,
    target_type: str | None = None,
    target_id: str | None = None,
    since: datetime | None = None,
    limit: int = 200,
) -> list[AuditLog]:
    stmt = select(AuditLog).where(AuditLog.tenant_id == tenant_id)
    if actor_id:
        stmt = stmt.where(AuditLog.actor_id == actor_id)
    if action:
        stmt = stmt.where(AuditLog.action == action)
    if target_type:
        stmt = stmt.where(AuditLog.target_type == target_type)
    if target_id:
        stmt = stmt.where(AuditLog.target_id == target_id)
    if since:
        stmt = stmt.where(AuditLog.created_at >= since)
    stmt = stmt.order_by(AuditLog.created_at.desc()).limit(min(limit, 1000))
    return list(db.scalars(stmt).all())
