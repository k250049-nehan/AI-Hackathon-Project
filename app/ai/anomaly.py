"""Lightweight anomaly detection for repeated claims and implausible amounts."""

from __future__ import annotations

import math

from app.normalization import name_similarity, normalize_cnic, safe_text

MODEL_VERSION = "anomaly-local-v1.0"


def detect_anomaly(
    claim: dict | None,
    past_claims: list[dict] | None,
    window_days: int = 30,
    max_duplicate_claims: int = 1,
) -> dict:
    """Return a 0..1 suspicion score with human-readable reasons.

    Flags are advisory: they send a case to a human, they never auto-reject it.
    """
    claim = claim or {}
    past = past_claims or []
    score = 0.0
    reasons: list[str] = []

    cnic = normalize_cnic(safe_text(claim.get("cnic")))
    if cnic:
        duplicates = sum(
            1
            for past_claim in past
            if normalize_cnic(safe_text(past_claim.get("cnic"))) == cnic
        )
        if duplicates >= max(1, max_duplicate_claims):
            score += 0.45
            reasons.append(f"Same CNIC appears in {duplicates} earlier claim(s) in the window.")

    amount = claim.get("claim_amount")
    if isinstance(amount, (int, float)):
        amounts = [
            float(item["claim_amount"])
            for item in past
            if isinstance(item.get("claim_amount"), (int, float)) and item.get("claim_amount") > 0
        ]
        if len(amounts) >= 3:
            mean = sum(amounts) / len(amounts)
            variance = sum((value - mean) ** 2 for value in amounts) / len(amounts)
            std = math.sqrt(variance)
            if std > 0 and amount > mean + 2 * std:
                score += 0.25
                reasons.append("Claim amount is more than two standard deviations above the norm.")

    name = safe_text(claim.get("full_name"))
    if name:
        near_matches = 0
        for past_claim in past:
            past_name = safe_text(past_claim.get("full_name"))
            past_cnic = normalize_cnic(safe_text(past_claim.get("cnic")))
            if name_similarity(name, past_name) >= 0.85 and past_cnic and past_cnic != cnic:
                near_matches += 1
        if near_matches >= 2:
            score += 0.30
            reasons.append("Similar name appears with multiple different CNIC numbers.")

    income = claim.get("monthly_income")
    if isinstance(amount, (int, float)) and isinstance(income, (int, float)) and income > 0:
        if amount > income * 3:
            score += 0.20
            reasons.append("Claim amount is high relative to declared income.")

    score = round(min(1.0, score), 4)
    return {
        "score": score,
        "flagged": score >= 0.45,
        "reasons": reasons,
        "model_version": MODEL_VERSION,
        "window_days": window_days,
        "simulated": True,
    }
