"""Structured outputs: extract form fields from messy text and validate them."""

from __future__ import annotations

import re

from pydantic import ValidationError

from app.normalization import normalize_cnic, normalize_name, safe_text
from app.schemas import ClaimForm

STRUCTURED_VERSION = "structured-claim-v1.0"


def extract_claim_from_text(text: str | None) -> dict:
    """Best-effort mock field extraction. Missing fields are reported, never invented."""
    clean = safe_text(text, 4000)
    extracted: dict = {}
    missing: list[str] = []

    cnic_match = re.search(r"\b\d{5}[-\s]?\d{7}[-\s]?\d\b", clean)
    if cnic_match:
        cnic = normalize_cnic(cnic_match.group(0))
        if cnic:
            extracted["cnic"] = cnic

    name_match = re.search(r"(?:my name is|i am|میرا نام)\s+([A-Za-z\u0600-\u06FF ]{3,60})", clean, re.I)
    if name_match:
        name = normalize_name(name_match.group(1))
        if name:
            extracted["full_name"] = name

    income_match = re.search(
        r"(?:monthly income|income|آمدنی)\s*(?:is|of|≈|=)?\s*(?:rs\.?\s*)?([\d,]{3,})",
        clean,
        re.I,
    )
    if income_match:
        extracted["monthly_income"] = int(income_match.group(1).replace(",", ""))

    dependents_match = re.search(r"([\d]{1,2})\s*(?:dependents|children|بچے)", clean, re.I)
    if dependents_match:
        extracted["dependents"] = int(dependents_match.group(1))

    amount_match = re.search(
        r"(?:claim(?:ing)?|need|request(?:ing)?|amount)\s*(?:of|for|rs\.?\s*)?([\d,]{3,})",
        clean,
        re.I,
    )
    if amount_match:
        extracted["claim_amount"] = int(amount_match.group(1).replace(",", ""))

    lowered = clean.lower()
    for category, keywords in {
        "widow": ("widow", "بیوہ"),
        "disabled": ("disabled", "معذور"),
        "unemployed": ("unemployed", "بے روزگار"),
        "low_income": ("low income", "low-income", "غربت"),
    }.items():
        if any(keyword in lowered for keyword in keywords):
            extracted["category"] = category
            break

    district_match = re.search(r"\b(?:in|from|district)\s+([A-Za-z\u0600-\u06FF]{3,40})", clean, re.I)
    if district_match:
        extracted["district"] = district_match.group(1).title()

    for field in ("full_name", "cnic", "monthly_income", "claim_amount", "district"):
        if field not in extracted:
            missing.append(field)
    extracted.setdefault("category", "low_income")
    extracted.setdefault("dependents", 0)

    return {
        "extracted": extracted,
        "missing_fields": missing,
        "complete": not missing,
        "model_version": STRUCTURED_VERSION,
        "simulated": True,
    }


def validate_claim(payload: dict) -> dict:
    """Validate a claim into a fixed, machine-checkable structure."""
    try:
        form = ClaimForm.model_validate(payload or {})
        return {
            "valid": True,
            "data": form.model_dump(),
            "errors": [],
            "model_version": STRUCTURED_VERSION,
        }
    except ValidationError as exc:
        errors = [
            {
                "field": ".".join(str(part) for part in error["loc"]),
                "message": error["msg"],
            }
            for error in exc.errors()
        ]
        return {
            "valid": False,
            "data": {},
            "errors": errors,
            "model_version": STRUCTURED_VERSION,
        }


VOICE_CLAIM_FIELDS = (
    "full_name", "cnic", "district", "category", "monthly_income",
    "claim_amount", "dependents",
)


def prepare_voice_claim(transcript: str | None, provided: dict | None) -> dict:
    """Merge explicit intake fields with transcript extraction before validation.

    When the citizen supplies labelled fields they win over guessed values. The
    merged claim is validated with the same ClaimForm used by /api/cases, so the
    rules, identity and anomaly checks all see one trustworthy structure.
    """
    extraction = extract_claim_from_text(transcript)
    if not isinstance(provided, dict):
        return {
            **extraction,
            "claim": dict(extraction["extracted"]),
            "valid": None,
            "errors": [],
        }

    def has_value(value: object) -> bool:
        return value is not None and str(value).strip() != ""

    explicit = {
        key: value
        for key, value in provided.items()
        if key in VOICE_CLAIM_FIELDS and has_value(value)
    }
    merged = {**extraction["extracted"], **explicit}
    validation = validate_claim(merged)
    claim = validation["data"] if validation["valid"] else merged
    return {
        **extraction,
        "extracted": claim,
        "claim": claim,
        "missing_fields": [] if validation["valid"] else list(extraction["missing_fields"]),
        "valid": validation["valid"],
        "errors": validation["errors"],
        "model_version": validation["model_version"],
    }
