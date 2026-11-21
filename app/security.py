"""Authentication, authorization and consent enforcement.

Every check here runs on the SERVER. Client-side checks are never trusted, so
raw curl calls are subject to exactly the same rules as the web interface.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.errors import AppError
from app.models import ApiKey, Consent, Tenant, User

PBKDF2_ITERATIONS = 180_000

bearer_scheme = HTTPBearer(auto_error=False)


# ---------------------------------------------------------------------------
# Passwords
# ---------------------------------------------------------------------------

def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt.hex()}${derived.hex()}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, iterations, salt_hex, digest_hex = encoded.split("$")
        if algorithm != "pbkdf2_sha256":
            return False
        derived = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), int(iterations)
        )
        return hmac.compare_digest(derived.hex(), digest_hex)
    except (ValueError, TypeError):
        return False


# ---------------------------------------------------------------------------
# JWT access tokens
# ---------------------------------------------------------------------------

def create_access_token(user: User) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user.id,
        "tenant_id": user.tenant_id,
        "role": user.role,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.access_token_ttl_minutes)).timestamp()),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError as exc:
        raise AppError(401, "invalid_token", "The access token is invalid or expired.") from exc


# ---------------------------------------------------------------------------
# API keys (public REST API)
# ---------------------------------------------------------------------------

def generate_api_key() -> tuple[str, str, str]:
    """Return (plain_key, prefix, sha256_hash). The plain key is shown once."""
    raw = secrets.token_urlsafe(32)
    plain = f"lm_{raw[:8]}_{raw}"
    return plain, raw[:8], hashlib.sha256(plain.encode("utf-8")).hexdigest()


def hash_api_key(plain: str) -> str:
    return hashlib.sha256(plain.encode("utf-8")).hexdigest()


def api_key_from_request(request: Request) -> str | None:
    value = request.headers.get("x-api-key")
    if value:
        return value.strip()
    authorization = request.headers.get("authorization", "")
    if authorization.lower().startswith("apikey "):
        return authorization[7:].strip()
    return None


# ---------------------------------------------------------------------------
# Authentication dependencies
# ---------------------------------------------------------------------------

def _user_from_jwt(db: Session, token: str) -> User | None:
    try:
        payload = decode_access_token(token)
    except AppError:
        return None
    user = db.get(User, str(payload.get("sub", "")))
    if not user or not user.is_active:
        return None
    return user


def _user_from_api_key(db: Session, plain: str) -> tuple[User, ApiKey] | None:
    key_hash = hash_api_key(plain)
    key = db.scalar(select(ApiKey).where(ApiKey.key_hash == key_hash, ApiKey.revoked.is_(False)))
    if not key:
        return None
    user = db.get(User, key.user_id)
    tenant = db.get(Tenant, key.tenant_id)
    if not user or not user.is_active or not tenant or not tenant.is_active:
        return None
    key.last_used_at = datetime.now(timezone.utc)
    db.add(key)
    db.flush()
    return user, key


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> User:
    """Accept a JWT bearer token OR an API key. Both are verified server-side."""
    if credentials and credentials.scheme.lower() == "bearer":
        user = _user_from_jwt(db, credentials.credentials)
        if user:
            return user
    plain_key = api_key_from_request(request)
    if plain_key:
        result = _user_from_api_key(db, plain_key)
        if result:
            return result[0]
    raise AppError(401, "authentication_required", "Sign in or provide a valid API key.")


def require_api_key(
    request: Request,
    db: Session = Depends(get_db),
) -> tuple[User, ApiKey]:
    """Public-API dependency: an API key is mandatory, JWT is not accepted."""
    plain = api_key_from_request(request)
    if not plain:
        raise AppError(401, "api_key_required", "Provide an API key in X-API-Key.")
    result = _user_from_api_key(db, plain)
    if not result:
        raise AppError(401, "invalid_api_key", "The API key is invalid or revoked.")
    return result


def api_key_with_scope(scope: str) -> Callable:
    def dependency(payload: tuple[User, ApiKey] = Depends(require_api_key)) -> tuple[User, ApiKey]:
        user, key = payload
        scopes = list(key.scopes or [])
        if "*" not in scopes and scope not in scopes:
            raise AppError(403, "scope_denied", f"API key lacks the '{scope}' scope.")
        return payload

    return dependency


def require_roles(*roles: str) -> Callable:
    """Factory for server-side role checks."""

    def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise AppError(
                403,
                "role_denied",
                f"This action requires one of: {', '.join(roles)}.",
                {"required_roles": list(roles), "your_role": user.role},
            )
        return user

    return dependency


CurrentUser = Annotated[User, Depends(get_current_user)]


# ---------------------------------------------------------------------------
# Tenant isolation and consent
# ---------------------------------------------------------------------------

def enforce_same_tenant(actor: User, tenant_id: str) -> None:
    if actor.tenant_id != tenant_id:
        raise AppError(404, "not_found", "Resource not found.")


def has_consent(
    db: Session,
    actor: User,
    subject_user_id: str,
    purpose: str,
    scope: str,
) -> bool:
    """True when the actor may access a subject's data for a given purpose."""
    if actor.id == subject_user_id:
        return True
    subject = db.get(User, subject_user_id)
    if subject is None or subject.tenant_id != actor.tenant_id:
        return False
    now = datetime.now(timezone.utc)
    records = db.scalars(
        select(Consent).where(
            Consent.subject_user_id == subject_user_id,
            Consent.status == "active",
            Consent.tenant_id == actor.tenant_id,
        )
    ).all()
    for record in records:
        if record.purpose != purpose:
            continue
        if scope not in (record.scopes or []):
            continue
        if record.grantee_user_id and record.grantee_user_id != actor.id:
            continue
        if record.grantee_role and record.grantee_role != actor.role:
            continue
        created_at = record.created_at
        if created_at is not None and getattr(created_at, "tzinfo", None) is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        if created_at and created_at > now:
            continue
        return True
    return False


def enforce_consent(
    db: Session,
    actor: User,
    subject_user_id: str,
    purpose: str,
    scope: str,
) -> None:
    """Raise 403 if consent is absent or withdrawn. Always audited by caller."""
    if not has_consent(db, actor, subject_user_id, purpose, scope):
        raise AppError(
            403,
            "consent_required",
            "Access denied: no active consent for this data and purpose.",
            {
                "subject_user_id": subject_user_id,
                "purpose": purpose,
                "required_scope": scope,
            },
        )


def consent_guard(purpose: str, scope: str, path_param: str = "subject_user_id") -> Callable:
    """Dependency that enforces consent using a path parameter on the request."""

    def dependency(
        request: Request,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user),
    ) -> User:
        subject = request.path_params.get(path_param)
        if subject:
            enforce_consent(db, user, str(subject), purpose, scope)
        return user

    return dependency
