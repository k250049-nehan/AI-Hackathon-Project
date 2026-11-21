"""Application configuration.

Everything is driven by environment variables with safe prototype defaults.
No real personal data and no external service credentials are required.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
# Vercel's serverless filesystem is read-only except /tmp. Keep the demo SQLite
# database there when running as a Vercel Function; local/dev keeps using data/.
if os.getenv("VERCEL") and "DATABASE_URL" not in os.environ:
    DATA_DIR = Path("/tmp/lastmile-data")
else:
    DATA_DIR = BASE_DIR / "data"
DOCS_DIR = BASE_DIR / "app" / "data" / "rules_docs"
STATIC_DIR = BASE_DIR / "app" / "static"

DATA_DIR.mkdir(parents=True, exist_ok=True)


def _bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass
class Settings:
    """Runtime settings, read once at import but overridable in tests."""

    app_name: str = "Last Mile - Relief Payment Platform (PROTOTYPE)"
    version: str = "1.0.0-prototype"
    environment: str = field(default_factory=lambda: os.getenv("APP_ENV", "prototype"))

    database_url: str = field(
        default_factory=lambda: os.getenv(
            "DATABASE_URL", f"sqlite:///{DATA_DIR / 'lastmile.db'}"
        )
    )
    secret_key: str = field(
        default_factory=lambda: os.getenv(
            "SECRET_KEY", "prototype-only-secret-key-not-for-production-0001"
        )
    )
    jwt_algorithm: str = "HS256"
    access_token_ttl_minutes: int = field(
        default_factory=lambda: int(os.getenv("ACCESS_TOKEN_TTL_MIN", "60"))
    )

    rate_limit_per_min: int = field(
        default_factory=lambda: int(os.getenv("RATE_LIMIT_PER_MIN", "120"))
    )
    auto_seed: bool = field(default_factory=lambda: _bool("AUTO_SEED", True))
    prototype_label: str = "PROTOTYPE - NOT AN OFFICIAL SERVICE - ALL DATA MOCKED"

    # Product-level cost trade-off. These are the published numbers behind the
    # "wrong approval vs slow approval" decision. They are used by the rule
    # engine and surfaced on the evaluation dashboard.
    cost_false_approve: float = 100.0
    cost_false_reject: float = 10.0
    cost_manual_review: float = 1.0
    auto_approve_min_confidence: float = 0.90
    ask_info_min_confidence: float = 0.65
    scam_block_confidence: float = 0.85


settings = Settings()
