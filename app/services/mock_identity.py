"""MOCK identity verification service (simulates NADRA-style lookup)."""

from __future__ import annotations

from app.normalization import name_similarity, normalize_cnic, safe_text
from app.services.mock_registry import MOCK_CITIZENS


def verify(cnic: str | None, full_name: str | None = None) -> dict:
    """Verify a fabricated identity without ever crashing on bad data."""
    digits = normalize_cnic(safe_text(cnic, 40))
    if not digits:
        return {
            "verified": False,
            "confidence": 0.0,
            "status": "incomplete",
            "reasons": ["CNIC is missing or malformed."],
            "mock": True,
            "simulated": True,
        }

    record = next((item for item in MOCK_CITIZENS if item["cnic"] == digits), None)
    if not record:
        return {
            "verified": False,
            "confidence": 0.15,
            "status": "not_found",
            "matched_name": None,
            "reasons": ["No mock identity record matches this CNIC."],
            "mock": True,
            "simulated": True,
        }

    provided = safe_text(full_name, 200)
    if not provided:
        return {
            "verified": False,
            "confidence": 0.50,
            "status": "needs_info",
            "matched_name": record["full_name"],
            "reasons": ["Applicant name is missing; ask for it before deciding."],
            "mock": True,
            "simulated": True,
        }

    similarity = name_similarity(provided, record["full_name"])
    if similarity >= 0.75:
        return {
            "verified": True,
            "confidence": 0.95 if similarity >= 0.95 else 0.88,
            "status": "verified",
            "matched_name": record["full_name"],
            "name_similarity": similarity,
            "reasons": ["Mock identity record found and name matches."],
            "mock": True,
            "simulated": True,
        }
    return {
        "verified": False,
        "confidence": 0.35,
        "status": "name_mismatch",
        "matched_name": record["full_name"],
        "name_similarity": similarity,
        "reasons": ["Name does not safely match the CNIC record; hand to a human."],
        "mock": True,
        "simulated": True,
    }
