"""Jev-style type-safe classification, confidence scoring and routing.

A scammer's message that merely mentions "relief payment" must NOT be blocked
on that word alone, so scam detection requires evidence from at least two
independent signal groups. Ambiguous cases get low confidence and are routed to
a human rather than guessed.
"""

from __future__ import annotations

import math
import re
import time

from app.normalization import safe_text

MODEL_VERSION = "jev-local-v1.2"
UNKNOWN_LABEL = "unknown"


def _patterns(*expressions: str) -> list[re.Pattern[str]]:
    return [re.compile(expr, re.IGNORECASE) for expr in expressions]


SCAM_GROUPS: dict[str, tuple[list[re.Pattern[str]], float]] = {
    "payment_lure": (
        _patterns(
            r"\b(relief|subsidy|aid|compensation) payment\b",
            r"\b(government|benazir|ehsaas|nadra|raast) (scheme|payment|grant)\b",
            r"\bcollect (your|the) (payment|money|cheque)\b",
        ),
        1.6,
    ),
    "suspicious_link": (
        _patterns(
            r"https?://\S+",
            r"\b(bit\.ly|tinyurl|t\.co|wa\.me|is\.gd)\b",
            r"\b(click|tap|open) (here|the link|this link|below)\b",
        ),
        1.7,
    ),
    "credential_request": (
        _patterns(
            r"\b(otp|one[-\s]?time password|pin code|password)\b",
            r"\b(send|share|enter|verify|confirm) (us |your )?(cnic|account|card|bank|otp|pin)\b",
            r"\bcnic (number|photo|copy)\b",
        ),
        1.9,
    ),
    "urgency_or_threat": (
        _patterns(
            r"\b(urgent|immediately|right now|within \d+ (hours|minutes)|last chance|expire[sd]?)\b",
            r"\b(blocked|suspended|disqualified|cancelled) (your )?(account|benefit|card)\b",
        ),
        1.2,
    ),
    "impersonation": (
        _patterns(
            r"\b(i am|this is) (from )?(nadra|raast|government|bank|benazir|ehsaas)\b",
            r"\bofficial (message|department|team)\b",
        ),
        1.1,
    ),
    "reward_lure": (
        _patterns(
            r"\b(congratulations|you have won|you are selected|guaranteed (payment|money))\b",
            r"\b(rs\.?\s?\d{4,}|[\$₨]\s?\d{4,})\b",
        ),
        0.9,
    ),
}

LEGITIMATE_SIGNALS: dict[str, tuple[list[re.Pattern[str]], float]] = {
    "relief_claim": (
        _patterns(
            r"\b(apply|application|claim|request)\b.{0,40}\b(relief|payment|benefit|subsidy|aid)\b",
            r"\b(monthly income|dependents|widow|disabled|unemployed|low income)\b",
            r"\b(cnic|district|income certificate)\b",
            r"\b(رلیف|ادائیگی|راشن|غربت|بیوہ)\b",
        ),
        1.0,
    ),
    "complaint": (
        _patterns(
            r"\b(complaint|grievance|problem|issue|unfair|wrong|delay|not received|never arrived)\b",
            r"\b(shikayat|شکایت|مسئلہ)\b",
        ),
        1.5,
    ),
    "request": (
        _patterns(
            r"\b(please (send|provide|help|tell|check)|how do i|what is the status|need help)\b",
            r"\b(status|update|information|guide|steps)\b",
        ),
        0.9,
    ),
}

DEFAULT_THRESHOLDS = {
    "auto_approve_min_confidence": 0.90,
    "ask_info_min_confidence": 0.65,
    "scam_block_confidence": 0.85,
}


def _score_text(text: str) -> tuple[dict[str, float], int]:
    scores: dict[str, float] = {label: 0.05 for label in ["scam", *LEGITIMATE_SIGNALS]}
    groups_matched = 0
    for group, (patterns, weight) in SCAM_GROUPS.items():
        hits = sum(1 for pattern in patterns if pattern.search(text))
        if hits:
            groups_matched += 1
            scores["scam"] += weight + 0.3 * (hits - 1)
    for label, (patterns, weight) in LEGITIMATE_SIGNALS.items():
        hits = sum(1 for pattern in patterns if pattern.search(text))
        if hits:
            scores[label] += weight + 0.3 * (hits - 1)

    # False-alarm control: mentioning a relief payment on its own (or paired
    # with a single credential word) is not enough to accuse a real citizen.
    if groups_matched < 2:
        scores["scam"] = min(scores["scam"], 0.40)

    # A complaint is a complaint even when it asks for a status update.
    if scores["complaint"] > 0.5:
        scores["complaint"] += 1.0
        scores["request"] = max(0.05, scores["request"] - 0.5)
    elif scores["relief_claim"] > 0.5:
        scores["relief_claim"] += 0.8
    elif scores["request"] > 0.5:
        scores["request"] += 0.5
    return scores, groups_matched


def classify(text: str | None, thresholds: dict | None = None) -> dict:
    """Classify untrusted text and return a confidence-scored routing decision."""
    started = time.perf_counter()
    clean = safe_text(text, 4000)
    thresholds = {**DEFAULT_THRESHOLDS, **(thresholds or {})}

    if not clean.strip():
        return {
            "label": UNKNOWN_LABEL,
            "confidence": 0.0,
            "scores": {},
            "route": "human_handoff",
            "reason": "No text was provided; a human must review the case.",
            "model_version": MODEL_VERSION,
            "simulated": True,
            "latency_ms": round((time.perf_counter() - started) * 1000, 3),
        }

    raw, groups_matched = _score_text(clean)
    ordered = sorted(raw.items(), key=lambda item: item[1], reverse=True)
    label, top_score = ordered[0]
    runner_up = ordered[1][1] if len(ordered) > 1 else 0.0
    margin = max(0.0, top_score - runner_up)

    confidence = 1.0 - math.exp(-0.8 * margin) if top_score > 0.10 else 0.10
    probabilities = {
        name: round(1.0 - math.exp(-0.8 * max(0.0, score - 0.05)), 4)
        for name, score in raw.items()
    }

    if label == "scam":
        # A single weak signal (e.g. "relief payment") is never enough to block.
        if groups_matched < 2:
            confidence = min(confidence, 0.55)

    if label == "scam":
        if confidence >= float(thresholds["scam_block_confidence"]):
            route = "auto_block"
            reason = "Multiple independent scam signals detected; message blocked before the citizen acts."
        elif confidence >= float(thresholds["ask_info_min_confidence"]):
            route = "ask_more_info"
            reason = "Possible scam, but evidence is incomplete; ask the citizen for more detail."
        else:
            route = "human_handoff"
            reason = "Uncertain scam signal; a human reviewer decides to avoid blocking a real person."
    elif label == UNKNOWN_LABEL or confidence < float(thresholds["ask_info_min_confidence"]):
        route = "human_handoff"
        reason = "Confidence is below the safe threshold; the case is handed to a human."
    elif label in {"relief_claim", "complaint"} and confidence < float(thresholds["auto_approve_min_confidence"]):
        route = "ask_more_info"
        reason = "The request looks genuine but needs more proof before any decision."
    elif confidence >= float(thresholds["auto_approve_min_confidence"]):
        route = "auto_handle"
        reason = "Classification confidence is high enough for automated handling of this step."
    else:
        route = "human_handoff"
        reason = "Uncertain classification; a human reviewer decides."

    return {
        "label": label,
        "confidence": round(confidence, 4),
        "scores": probabilities,
        "route": route,
        "reason": reason,
        "model_version": MODEL_VERSION,
        "simulated": True,
        "signal_groups": groups_matched,
        "latency_ms": round((time.perf_counter() - started) * 1000, 3),
    }
