"""Administration: users, roles, API keys, tenants, webhooks and notifications."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.audit import log
from app.db import get_db
from app.errors import AppError
from app.models import ApiKey, Notification, Tenant, User, Webhook, new_id
from app.schemas import ApiKeyCreate, ApiKeyOut, UserCreate, UserOut, WebhookCreate, WebhookOut
from app.security import generate_api_key, get_current_user, require_roles
from app.services.mock_data import list_mock_families

from app.api.helpers import actor_label

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users", response_model=list[UserOut], summary="List workspace users")
def list_users(
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles("admin")),
) -> list[UserOut]:
    rows = db.scalars(select(User).where(User.tenant_id == actor.tenant_id)).all()
    return [UserOut.model_validate(row) for row in rows]


@router.post("/users", response_model=UserOut, status_code=201, summary="Create a mock user")
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles("admin")),
) -> UserOut:
    email = payload.email.strip().lower()
    if db.scalar(select(User).where(User.email == email)):
        raise AppError(409, "email_taken", "That email already exists.")
    from app.security import hash_password

    user = User(
        tenant_id=actor.tenant_id,
        email=email,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
        role=payload.role,
        phone=payload.phone,
        preferred_language=payload.preferred_language,
    )
    db.add(user)
    db.flush()
    log(
        db,
        tenant_id=actor.tenant_id,
        actor_type="user",
        actor_id=actor.id,
        action="user.created",
        target_type="user",
        target_id=user.id,
        detail={"role": payload.role, "actor": actor_label(actor)},
    )
    db.commit()
    return UserOut.model_validate(user)


@router.post("/api-keys", response_model=ApiKeyOut, status_code=201, summary="Create a public API key")
def create_api_key(
    payload: ApiKeyCreate,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles("admin")),
) -> ApiKeyOut:
    plain, prefix, digest = generate_api_key()
    key = ApiKey(
        tenant_id=actor.tenant_id,
        user_id=actor.id,
        name=payload.name,
        prefix=prefix,
        key_hash=digest,
        scopes=payload.scopes,
    )
    db.add(key)
    db.flush()
    log(
        db,
        tenant_id=actor.tenant_id,
        actor_type="user",
        actor_id=actor.id,
        action="api_key.created",
        target_type="api_key",
        target_id=key.id,
        detail={"scopes": payload.scopes, "prefix": prefix},
    )
    db.commit()
    return ApiKeyOut(
        id=key.id,
        name=key.name,
        prefix=prefix,
        plain_key=plain,
        scopes=key.scopes,
    )


@router.get("/api-keys", summary="List API key metadata (never returns secrets)")
def list_api_keys(
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles("admin")),
) -> list[dict]:
    keys = db.scalars(select(ApiKey).where(ApiKey.tenant_id == actor.tenant_id)).all()
    return [
        {
            "id": key.id,
            "name": key.name,
            "prefix": key.prefix,
            "scopes": key.scopes,
            "revoked": key.revoked,
            "last_used_at": key.last_used_at,
        }
        for key in keys
    ]


@router.post("/api-keys/{key_id}/revoke", summary="Revoke an API key")
def revoke_api_key(
    key_id: str,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles("admin")),
) -> dict:
    key = db.get(ApiKey, key_id)
    if not key or key.tenant_id != actor.tenant_id:
        raise AppError(404, "not_found", "API key not found.")
    key.revoked = True
    log(
        db,
        tenant_id=actor.tenant_id,
        actor_type="user",
        actor_id=actor.id,
        action="api_key.revoked",
        target_type="api_key",
        target_id=key.id,
        detail={"prefix": key.prefix},
    )
    db.commit()
    return {"revoked": True, "key_id": key.id}


@router.get("/tenants", summary="List workspaces")
def list_tenants(
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> list[dict]:
    tenants = db.scalars(select(Tenant).where(Tenant.id == actor.tenant_id)).all()
    return [
        {"id": tenant.id, "name": tenant.name, "slug": tenant.slug, "plan": tenant.plan}
        for tenant in tenants
    ]


@router.post("/webhooks", response_model=WebhookOut, status_code=201)
def create_webhook(
    payload: WebhookCreate,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles("admin")),
) -> WebhookOut:
    hook = Webhook(
        id=new_id(),
        tenant_id=actor.tenant_id,
        url=payload.url,
        event_types=payload.event_types,
        is_active=True,
    )
    db.add(hook)
    db.flush()
    log(
        db,
        tenant_id=actor.tenant_id,
        actor_type="user",
        actor_id=actor.id,
        action="webhook.created",
        target_type="webhook",
        target_id=hook.id,
        detail={"event_types": payload.event_types},
    )
    db.commit()
    return WebhookOut.model_validate(hook)


@router.get("/webhooks", response_model=list[WebhookOut])
def list_webhooks(
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles("admin")),
) -> list[WebhookOut]:
    hooks = db.scalars(select(Webhook).where(Webhook.tenant_id == actor.tenant_id)).all()
    return [WebhookOut.model_validate(hook) for hook in hooks]


@router.get("/helper-families", summary="Helper Mode: 40 mock families on one phone")
def helper_families(
    actor: User = Depends(require_roles("helper", "admin")),
) -> dict:
    return {
        "helper_id": actor.id,
        "families": list_mock_families(),
        "notice": "Each family needs its own consent. mock=True.",
        "mock": True,
    }


@router.get("/notifications", summary="Notifications for the signed-in user")
def notifications(
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> list[dict]:
    rows = db.scalars(
        select(Notification).where(Notification.user_id == actor.id).order_by(Notification.created_at.desc()).limit(50)
    ).all()
    return [
        {
            "id": row.id,
            "channel": row.channel,
            "title": row.title,
            "body": row.body,
            "status": row.status,
            "created_at": row.created_at,
        }
        for row in rows
    ]
