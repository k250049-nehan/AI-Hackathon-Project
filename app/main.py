"""FastAPI application entry point for the prototype platform."""

from __future__ import annotations

import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api import (
    admin,
    ai_api,
    audit_api,
    auth,
    cases,
    consent_api,
    eval_api,
    mock_api,
    public,
    rules,
    sync,
)
from app.config import STATIC_DIR, settings
from app.data.seed import seed_database
from app.db import SessionLocal, init_db
from app.errors import AppError

DESCRIPTION = """
**PROTOTYPE - NOT AN OFFICIAL SERVICE.** All citizens, CNICs, identity records,
payments and policy documents are mocked. No real personal data is used.

This platform helps a low-literacy citizen or community helper complete a
**relief-payment claim** on a weak connection, using voice or text, while the
system decides, explains, protects, and hands uncertain cases to a human.

- JWT login + server-side RBAC and consent
- Versioned rules that change without redeploy
- Jev-style classification with confidence routing
- Local RAG over bundled mock policy documents with sources
- Deterministic structured outputs, OCR/QR checks and anomaly detection
- Two-view explainability and a full audit trail
- Offline-first idempotent sync and a Digital Twin rule simulator
"""


@asynccontextmanager
async def lifespan(application: FastAPI):
    init_db()
    if settings.auto_seed:
        with SessionLocal() as db:
            seed_database(db)
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description=DESCRIPTION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


def _openapi_schema():
    """Document both auth mechanisms in Swagger for raw API testing."""
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=DESCRIPTION,
        routes=app.routes,
    )
    components = schema.setdefault("components", {})
    schemes = components.setdefault("securitySchemes", {})
    schemes["BearerAuth"] = {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    schemes["ApiKeyAuth"] = {"type": "apiKey", "in": "header", "name": "X-API-Key"}
    for path, operations in schema.get("paths", {}).items():
        for method, operation in operations.items():
            if not isinstance(operation, dict):
                continue
            if path.startswith("/api/public"):
                operation["security"] = [{"ApiKeyAuth": []}]
            elif path.startswith("/api/") and not path.startswith("/api/auth/login"):
                operation.setdefault("security", [{"BearerAuth": []}, {"ApiKeyAuth": []}])
    app.openapi_schema = schema
    return schema


app.openapi = _openapi_schema


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.code,
            "message": exc.message,
            "details": exc.details,
            "prototype": True,
            "official_service": False,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "message": "The request does not match the expected structure.",
            "details": exc.errors(),
            "prototype": True,
        },
    )


class RateLimitMiddleware:
    """Small in-memory sliding-window limiter; protects the public API."""

    def __init__(self, app):
        self.app = app
        self.hits: dict[str, deque[float]] = defaultdict(deque)

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or not scope["path"].startswith("/api/"):
            await self.app(scope, receive, send)
            return
        headers = dict(scope.get("headers", []))
        client_ip = scope.get("client", ("unknown", 0))[0] or "unknown"
        api_key = headers.get(b"x-api-key", b"").decode("utf-8", "ignore")
        explicit = headers.get(b"x-client-id", b"").decode("utf-8", "ignore")
        identity = explicit or (api_key[-12:] if api_key else client_ip)
        key = (identity, scope["path"].split("/")[2] if len(scope["path"].split("/")) > 2 else "api")
        now = time.monotonic()
        bucket = self.hits[key]
        while bucket and now - bucket[0] > 60:
            bucket.popleft()
        if len(bucket) >= settings.rate_limit_per_min:
            response = JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limited",
                    "message": "Too many requests. Slow down and retry shortly.",
                    "prototype": True,
                },
            )
            await response(scope, receive, send)
            return
        bucket.append(now)
        await self.app(scope, receive, send)


app.add_middleware(RateLimitMiddleware)

for router in (
    auth.router,
    cases.router,
    rules.router,
    consent_api.router,
    audit_api.router,
    admin.router,
    ai_api.router,
    public.router,
    sync.router,
    eval_api.router,
    mock_api.router,
):
    app.include_router(router)

STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/health", tags=["ops"], summary="Liveness and prototype notice")
def health() -> dict:
    return {
        "status": "ok",
        "service": settings.app_name,
        "prototype": True,
        "official_service": False,
        "real_personal_data": False,
    }


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    path = Path(STATIC_DIR) / "index.html"
    if not path.exists():
        return JSONResponse(
            status_code=503,
            content={"error": "ui_not_built", "message": "Static UI is missing.", "prototype": True},
        )
    return FileResponse(str(path))
