"""Defensive normalization for messy real-world inputs.

Handles missing fields, repeated separators and the classic
Muhammad / Mohammad / Muhammed spelling explosion without ever guess-matching
two different people.
"""

from __future__ import annotations

import difflib
import re
import unicodedata

NAME_ALIASES = {
    "muhammad": "muhammad",
    "mohammad": "muhammad",
    "muhammed": "muhammad",
    "mohammed": "muhammad",
    "muhamed": "muhammad",
    "mohamed": "muhammad",
    "mohd": "muhammad",
    "md": "muhammad",
    "fatima": "fatima",
    "fatma": "fatima",
    "fatimah": "fatima",
    "aisha": "aisha",
    "aishah": "aisha",
    "usman": "usman",
    "othman": "usman",
    "abdullah": "abdullah",
    "abdulla": "abdullah",
    "bibi": "bibi",
    "begum": "begum",
    "khawaja": "khawaja",
}


def normalize_name(value: str | None) -> str:
    if not value or not isinstance(value, str):
        return ""
    ascii_text = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    tokens = re.findall(r"[a-z]+", ascii_text.lower())
    return " ".join(NAME_ALIASES.get(token, token) for token in tokens)


def name_similarity(left: str | None, right: str | None) -> float:
    """Return 0..1 similarity. Requires BOTH names to be present."""
    a, b = normalize_name(left), normalize_name(right)
    if not a or not b:
        return 0.0
    a_tokens, b_tokens = set(a.split()), set(b.split())
    jaccard = len(a_tokens & b_tokens) / len(a_tokens | b_tokens) if (a_tokens | b_tokens) else 0.0
    sequence = difflib.SequenceMatcher(None, a, b).ratio()
    return round(max(jaccard, sequence), 3)


def normalize_cnic(value: str | None) -> str:
    """Return 13-digit CNIC, or '' for missing/malformed input."""
    if not value or not isinstance(value, str):
        return ""
    digits = re.sub(r"\D", "", value)
    return digits if len(digits) == 13 else ""


def format_cnic(value: str | None) -> str:
    digits = normalize_cnic(value)
    if not digits:
        return ""
    return f"{digits[:5]}-{digits[5:12]}-{digits[12]}"


def safe_text(value: object, max_length: int = 4000) -> str:
    """Coerce untrusted input into bounded text without raising."""
    if value is None:
        return ""
    text = str(value)
    text = "".join(ch for ch in text if ch.isprintable() or ch in "\n\t")
    return text[:max_length]


def clean_dict(value: object) -> dict:
    if not isinstance(value, dict):
        return {}
    return {str(k)[:80]: safe_text(v) if isinstance(v, (str, int, float)) else v for k, v in value.items()}
