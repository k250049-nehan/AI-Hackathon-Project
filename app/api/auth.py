"""Login and current-user endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.audit import log
from app.db import get_db
from app.errors import AppError
from app.models import User
from app.schemas import LoginRequest, TokenResponse, UserOut
from app.security import create_access_token, get_current_user, verify_password
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse, summary="Sign in with a mock account")
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.query(User).filter(User.email == payload.email.strip().lower()).first()
    if not user or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise AppError(401, "invalid_credentials", "Email or password is incorrect.")
    log(
        db,
        tenant_id=user.tenant_id,
        actor_type="user",
        actor_id=user.id,
        action="auth.login",
        target_type="user",
        target_id=user.id,
        detail={"role": user.role, "simulated": True},
    )
    db.commit()
    return TokenResponse(
        access_token=create_access_token(user),
        expires_in=settings.access_token_ttl_minutes * 60,
        user_id=user.id,
        tenant_id=user.tenant_id,
        role=user.role,
    )


@router.get("/me", response_model=UserOut, summary="Inspect the authenticated principal")
def me(user: User = Depends(get_current_user)) -> UserOut:
    return UserOut.model_validate(user)
