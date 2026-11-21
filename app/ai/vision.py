"""MOCK document OCR, QR and forgery checks.

No image model or real document is used. Input text is treated as simulated
OCR output so the full flow can be demonstrated offline.
"""

from __future__ import annotations

import re

from app.normalization import normalize_cnic, safe_text

MODEL_VERSION = "vision-mock-v1.0"


def analyze(
    ocr_text: str | None,
    *,
    qr_valid: bool | None = None,
    blurry: bool = False,
    expected_cnic: str | None = None,
) -> dict:
    text = safe_text(ocr_text, 4000)
    reasons: list[str] = []
    score = 0.0

    if not text:
        reasons.append("No readable text was extracted; a human must inspect the image.")
        score += 0.35
    if len(text) < 12 and text:
        reasons.append("Very little text was detected; image may be blurry.")
        score += 0.25
    if blurry:
        reasons.append("Image reported as blurry; do not auto-reject the document.")
        score += 0.25

    found_cnic = normalize_cnic(text)
    expected = normalize_cnic(expected_cnic)
    if expected and found_cnic and found_cnic != expected:
        reasons.append("CNIC in the document differs from the claim.")
        score += 0.45
    if expected and not found_cnic:
        reasons.append("CNIC could not be read from the document.")
        score += 0.15

    if re.search(r"\b(edited|photoshopped|photocopy|not valid|specimen|sample)\b", text, re.I):
        reasons.append("Document contains an editing or specimen marker.")
        score += 0.50
    if qr_valid is False:
        reasons.append("QR code did not validate.")
        score += 0.40
    if qr_valid is None:
        reasons.append("QR code was not checked.")
        score += 0.10

    score = round(min(1.0, score), 4)
    return {
        "ocr_text": text,
        "qr_valid": qr_valid,
        "forgery_score": score,
        "suspicious": score >= 0.50,
        "route": "human_review" if score >= 0.50 else "auto_handle",
        "reasons": reasons or ["Document checks passed in the mock analysis."],
        "model_version": MODEL_VERSION,
        "simulated": True,
    }
