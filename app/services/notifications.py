"""In-app notifications (SMS/WhatsApp/email are simulated channels)."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.audit import log
from app.models import Notification, new_id


def notify(
    db: Session,
    *,
    tenant_id: str,
    user_id: str,
    title: str,
    body: str,
    channel: str = "in_app",
    actor_id: str = "system",
) -> Notification:
    notification = Notification(
        id=new_id(),
        tenant_id=tenant_id,
        user_id=user_id,
        channel=channel,
        title=title[:160],
        body=body[:2000],
        status="queued",
    )
    db.add(notification)
    db.flush()
    log(
        db,
        tenant_id=tenant_id,
        actor_type="system",
        actor_id=actor_id,
        action="notification.queued",
        target_type="notification",
        target_id=notification.id,
        detail={"channel": channel, "user_id": user_id, "simulated": True},
    )
    return notification
