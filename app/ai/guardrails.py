"""Safety guardrails and the human-approval gate."""

from __future__ import annotations

import re

from app.normalization import safe_text

INJECTION_PATTERNS = [
    re.compile(r"ignore (all )?(previous|prior|above) instructions", re.I),
    re.compile(r"reveal (your )?(system|developer) prompt", re.I),
    re.compile(r"disregard (the )?(rules|policy|safety)", re.I),
]

CNIC_PATTERN = re.compile(r"\b\d{5}[-\s]?\d{7}[-\s]?\d\b")
PHONE_PATTERN = re.compile(r"\b(03\d{2}[-\s]?\d{7}|\+92[\s-]?3\d{2}[-\s]?\d{7})\b")


def redact_pii(text: str | None) -> str:
    """Never echo full CNIC or phone numbers back to a user-facing surface."""
    clean = safe_text(text, 4000)
    clean = CNIC_PATTERN.sub("•••••-•••••••-•", clean)
    clean = PHONE_PATTERN.sub("•••-•••••••", clean)
    return clean


def check_output(text: str | None) -> dict:
    """Block unsafe AI output before it reaches a citizen."""
    clean = safe_text(text, 4000)
    reasons = []
    for pattern in INJECTION_PATTERNS:
        if pattern.search(clean):
            reasons.append("prompt_injection")
    if CNIC_PATTERN.search(clean) or PHONE_PATTERN.search(clean):
        reasons.append("unredacted_personal_data")
    return {
        "allowed": not reasons,
        "reasons": reasons,
        "redacted_text": redact_pii(clean),
    }


def requires_human_approval(
    action: str,
    confidence: float,
    definition: dict | None = None,
) -> tuple[bool, str]:
    """Decide whether a risky/uncertain step must wait for an officer.

    Payment disbursement is ALWAYS gated, even at high confidence, because a
    wrong approval costs far more than a slow one.
    """
    definition = definition or {}
    always_gated = {"disburse_payment", "approve_claim", "close_case"}
    if action in always_gated or definition.get("require_officer_for_payment", True):
        if action == "disburse_payment":
            return True, "Payment disbursement always requires officer approval."
        if action == "approve_claim":
            return True, "Claim approval is a high-cost decision and requires officer approval."
    threshold = float(definition.get("auto_approve_min_confidence", 0.90))
    if confidence < threshold:
        return True, f"Confidence {confidence:.2f} is below the auto-act threshold {threshold:.2f}."
    return False, "Confidence is high enough and the step is not high-risk."
