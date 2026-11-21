"""Tiny local retrieval-augmented generator over bundled MOCK policy docs.

No embedding API is used. Retrieval is TF-IDF over document sections, and every
answer carries its sources so a citizen or auditor can verify the claim.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from app.ai.guardrails import redact_pii
from app.config import DOCS_DIR

TOKEN_PATTERN = re.compile(r"[^\W_]+", re.UNICODE)


@dataclass(frozen=True)
class Chunk:
    document: str
    section: str
    text: str
    tokens: tuple[str, ...]


def _tokenize(text: str) -> tuple[str, ...]:
    return tuple(token.lower() for token in TOKEN_PATTERN.findall(text or ""))


def _load_chunks() -> list[Chunk]:
    chunks: list[Chunk] = []
    for path in sorted(DOCS_DIR.glob("*.md")):
        content = path.read_text(encoding="utf-8")
        sections = re.split(r"^##\s+", content, flags=re.MULTILINE)
        for section in sections:
            if not section.strip():
                continue
            lines = section.strip().splitlines()
            title = lines[0].strip() if lines else path.name
            body = "\n".join(lines[1:]).strip()
            if not body:
                body = title
            chunks.append(
                Chunk(
                    document=path.name,
                    section=title[:120],
                    text=body,
                    tokens=_tokenize(body),
                )
            )
    return chunks


_CHUNKS = _load_chunks()
_IDF: dict[str, float] = {}
for _chunk in _CHUNKS:
    for _token in set(_chunk.tokens):
        _IDF[_token] = _IDF.get(_token, 0.0) + 1.0
for _token in list(_IDF):
    _IDF[_token] = math.log((1 + len(_CHUNKS)) / (1 + _IDF[_token])) + 1.0


def retrieve(question: str, top_k: int = 3) -> list[dict]:
    """Return the most relevant mock-policy passages with similarity scores."""
    query_tokens = _tokenize(question)
    if not query_tokens:
        return []
    scored = []
    for chunk in _CHUNKS:
        counts = Counter(chunk.tokens)
        score = sum(_IDF.get(token, 0.0) * counts.get(token, 0) for token in query_tokens)
        if score <= 0:
            continue
        normalizer = math.sqrt(sum((_IDF.get(token, 1.0) * count) ** 2 for token, count in counts.items()))
        score = score / normalizer if normalizer else 0.0
        scored.append((score, chunk))
    scored.sort(key=lambda item: item[0], reverse=True)
    top = scored[: max(1, min(top_k, 6))]
    if not top:
        return []
    best = top[0][0] or 1.0
    return [
        {
            "document": chunk.document,
            "section": chunk.section,
            "quote": chunk.text[:600],
            "relevance": round(score / best, 4),
        }
        for score, chunk in top
    ]


def answer(question: str, top_k: int = 3) -> dict:
    """Answer strictly from bundled mock documents, never from free-form memory."""
    sources = retrieve(question, top_k)
    if not sources:
        return {
            "answer": "I could not find a matching rule in the mock policy documents. "
            "I am not sure, so I am handing this question to a human reviewer.",
            "sources": [],
            "simulated": True,
            "uncertain": True,
        }

    is_urdu = bool(re.search(r"[\u0600-\u06FF]", question))
    intro = (
        "دستاویزات میں درج معلومات کے مطابق:\n" if is_urdu
        else "Based on the mock policy documents provided:\n"
    )
    parts = [intro]
    for index, source in enumerate(sources, start=1):
        quote = redact_pii(source["quote"])
        parts.append(f"[{index}] {quote}\n    (Source: {source['document']} - {source['section']})")
    if is_urdu:
        parts.append("\nیہ صرف ایک پروٹوٹائپ ہے۔ حتمی فیصلہ انسانی جائزہ کار کرے گا۔")
    else:
        parts.append("\nThis is a prototype. A human officer makes the final decision.")
    return {
        "answer": "\n\n".join(parts),
        "sources": sources,
        "simulated": True,
        "uncertain": False,
    }
