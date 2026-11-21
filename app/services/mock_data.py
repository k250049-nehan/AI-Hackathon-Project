"""MOCK data-exchange service (simulates a consented data-sharing gateway)."""

from __future__ import annotations

from app.normalization import normalize_cnic, safe_text
from app.services.mock_registry import MOCK_CITIZENS


def get_record(cnic: str | None) -> dict:
    digits = normalize_cnic(safe_text(cnic, 40))
    record = next((item for item in MOCK_CITIZENS if item["cnic"] == digits), None)
    if not record:
        return {
            "found": False,
            "data": {},
            "missing_fields": ["record"],
            "mock": True,
            "simulated": True,
        }
    return {
        "found": True,
        "data": dict(record),
        "missing_fields": list(record.get("missing_fields", [])),
        "mock": True,
        "simulated": True,
    }


def list_mock_families() -> list[dict]:
    from app.services.mock_registry import MOCK_HELPER_FAMILIES

    return [dict(item) for item in MOCK_HELPER_FAMILIES]
