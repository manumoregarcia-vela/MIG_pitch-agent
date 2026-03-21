from __future__ import annotations

import re
from collections import Counter
from typing import Any

PDF_INTERNAL_TOKENS = [
    "obj",
    "/Page",
    "/XObject",
    "FlateDecode",
    "BitsPerComponent",
    "ColorSpace",
    "Length",
]

TECHNICAL_TOKEN_PATTERN = re.compile(
    r"(?:/[A-Za-z][\w#.-]*|\b\d+\s+\d+\s+obj\b|\bendobj\b|\bstream\b|\bendstream\b|<<|>>|\bR\b)",
    flags=re.IGNORECASE,
)

WORD_PATTERN = re.compile(r"[A-Za-z][A-Za-z'\-]{2,}")
SENTENCE_PATTERN = re.compile(r"[^\n.!?]{20,}[.!?]")


def _safe_ratio(numerator: float, denominator: float) -> float:
    if denominator <= 0:
        return 0.0
    return numerator / denominator


def assess_extraction_quality(raw_text: str) -> dict[str, Any]:
    text = raw_text or ""
    total_chars = len(text)
    total_words = WORD_PATTERN.findall(text)
    total_word_count = len(total_words)

    token_counts = Counter()
    for token in PDF_INTERNAL_TOKENS:
        token_counts[token] = len(re.findall(re.escape(token), text, flags=re.IGNORECASE))

    pdf_internal_count = sum(token_counts.values())
    technical_token_count = len(TECHNICAL_TOKEN_PATTERN.findall(text))

    meaningful_words = [
        word for word in total_words if word.lower() not in {"obj", "endobj", "stream", "endstream", "xref", "trailer"}
    ]
    meaningful_sentence_count = len(SENTENCE_PATTERN.findall(text))

    natural_language_ratio = _safe_ratio(len(meaningful_words), max(total_word_count, 1))
    technical_token_ratio = _safe_ratio(technical_token_count, max(total_word_count, 1))
    pdf_internal_density = _safe_ratio(pdf_internal_count, max(total_chars, 1))

    reasons: list[str] = []

    if total_chars < 500:
        reasons.append("Very little extractable text")
    if pdf_internal_count >= 20 or pdf_internal_density > 0.01:
        reasons.append("High presence of PDF internal structure tokens")
    if natural_language_ratio < 0.55:
        reasons.append("Low ratio of natural language words")
    if technical_token_ratio > 0.35:
        reasons.append("High ratio of technical/PDF tokens")
    if meaningful_sentence_count < 3:
        reasons.append("Low number of meaningful sentences")

    quality = "poor" if reasons else "good"

    return {
        "quality": quality,
        "reasons": reasons,
        "scores": {
            "total_chars": total_chars,
            "total_word_count": total_word_count,
            "pdf_internal_count": pdf_internal_count,
            "pdf_internal_density": round(pdf_internal_density, 4),
            "natural_language_ratio": round(natural_language_ratio, 4),
            "technical_token_count": technical_token_count,
            "technical_token_ratio": round(technical_token_ratio, 4),
            "meaningful_sentence_count": meaningful_sentence_count,
            "internal_token_breakdown": dict(token_counts),
        },
    }
