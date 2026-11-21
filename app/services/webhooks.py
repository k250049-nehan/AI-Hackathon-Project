"""Outbound webhooks with recorded delivery attempts (mock-friendly)."""

from __future__ import annotations

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.audit import log
from app.models import Webhook, WebhookDelivery, new_id

TIMEOUT_SECONDS = 1.0


def dispatch(db: Session, *, tenant_id: str, event: str, payload: dict) -> list[WebhookDelivery]:
    """Attempt delivery to every active subscribed webhook and log the result."""
    hooks = db.scalars(
        select(Webhook).where(
            Webhook.tenant_id == tenant_id,
            Webhook.is_active.is_(True),
        )
    ).all()
    deliveries: list[WebhookDelivery] = []
    for hook in hooks:
        if event not in (hook.event_types or []):
            continue
        delivery = WebhookDelivery(
            id=new_id(),
            tenant_id=tenant_id,
            webhook_id=hook.id,
            event=event,
            payload=payload,
            status="attempted",
        )
        try:
            response = httpx.post(hook.url, json=payload, timeout=TIMEOUT_SECONDS)
            delivery.response_code = response.status_code
            delivery.status = "delivered" if response.status_code < 400 else "failed"
        except Exception as exc:  # network failures are recorded, never fatal
            delivery.status = "failed"
            delivery.payload = {**payload, "delivery_error": type(exc).__name__}
        db.add(delivery)
        db.flush()
        log(
            db,
            tenant_id=tenant_id,
            actor_type="system",
            actor_id="webhook",
            action="webhook.delivered",
            target_type="webhook",
            target_id=hook.id,
            detail={"event": event, "status": delivery.status},
        )
        deliveries.append(delivery)
    return deliveries
