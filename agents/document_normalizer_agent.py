from __future__ import annotations

import os
import re
from typing import Any

from agents.document_ingestion_agent import build_normalized_input, parse_studio_document
from agents.document_llm_normalizer_agent import normalize_text_to_structured_input


def _empty_normalized_template(source_file: str, mode: str) -> dict[str, Any]:
    return {
        "studio_profile": {"studio_name": ""},
        "game_profile": {
            "game_name": "",
            "genre": "",
            "platforms": [],
            "development_stage": "",
            "core_fantasy": "",
        },
        "traction": {},
        "business": {
            "business_model": "",
            "target_audience": "",
            "current_ask": "",
            "funding_status": "",
        },
        "team": [],
        "assets": {},
        "known_gaps": [],
        "source_map": {
            "document": source_file,
            "ingestion_mode": mode,
        },
    }


def _collect_text_snippets(raw_text: str, page_hints: list[dict[str, Any]]) -> list[str]:
    snippets: list[str] = []

    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    for line in lines:
        if 20 <= len(line) <= 220:
            snippets.append(line)
        if len(snippets) >= 20:
            break

    for hint in page_hints:
        sample = hint.get("sample_text", "").strip()
        if sample:
            snippets.append(f"[page {hint.get('page')}] {sample[:220]}")

    deduped: list[str] = []
    seen = set()
    for item in snippets:
        key = re.sub(r"\s+", " ", item.lower())
        if key and key not in seen:
            seen.add(key)
            deduped.append(item)

    return deduped[:25]


def _fallback_normalize_document(
    raw_text: str,
    source_file: str,
    quality_report: dict[str, Any],
    page_hints: list[dict[str, Any]],
) -> dict[str, Any]:
    # Compact representation intended for hybrid/LLM-assisted normalization in future iterations.
    snippets = _collect_text_snippets(raw_text, page_hints)
    compact_representation = {
        "source_file": source_file,
        "quality_reasons": quality_report.get("reasons", []),
        "snippets": snippets,
        "page_hints": page_hints,
    }

    seed_text = "\n".join(snippets)
    parsed = parse_studio_document(seed_text, source_file=source_file)

    normalized = _empty_normalized_template(source_file=source_file, mode="hybrid-fallback")
    normalized_from_rules = build_normalized_input(parsed, source_file=source_file)

    # Keep only confidently extracted values from compact snippets.
    normalized["studio_profile"] = normalized_from_rules.get("studio_profile", normalized["studio_profile"])
    normalized["game_profile"] = normalized_from_rules.get("game_profile", normalized["game_profile"])
    normalized["traction"] = normalized_from_rules.get("traction", {})
    normalized["business"] = normalized_from_rules.get("business", normalized["business"])
    normalized["team"] = normalized_from_rules.get("team", [])
    normalized["assets"] = normalized_from_rules.get("assets", {})

    normalized["source_map"].update(
        {
            "normalization_mode": "hybrid-fallback",
            "compact_representation": compact_representation,
        }
    )

    normalized["known_gaps"] = list(normalized_from_rules.get("known_gaps", []))
    normalized["known_gaps"].append("Fallback mode used due to poor extraction quality")

    return normalized


def _llm_normalize_document(
    raw_text: str,
    source_file: str,
    quality_report: dict[str, Any],
    page_hints: list[dict[str, Any]],
    strict_llm: bool = False,
) -> tuple[dict[str, Any], dict[str, Any]]:
    try:
        return normalize_text_to_structured_input(raw_text=raw_text, source_file=source_file)
    except Exception as exc:
        if strict_llm:
            raise RuntimeError(
                "Strict LLM normalization is enabled and real LLM normalization failed."
            ) from exc
        snippets = _collect_text_snippets(raw_text, page_hints)
        seed_text = "\n".join(snippets)
        parsed = parse_studio_document(seed_text, source_file=source_file)
        normalized = build_normalized_input(parsed, source_file=source_file)
        normalized.setdefault("source_map", {}).update(
            {
                "normalization_mode": "hybrid-fallback",
                "llm_used": False,
                "llm_error": str(exc),
            }
        )
        llm_artifact = {
            "mode": "hybrid-fallback",
            "provider": "openai",
            "llm_used": False,
            "error": str(exc),
            "normalized_output": normalized,
        }
        return normalized, llm_artifact


def normalize_document_content(
    raw_text: str,
    source_file: str,
    quality_report: dict[str, Any],
    page_hints: list[dict[str, Any]] | None = None,
    source_map_overrides: dict[str, Any] | None = None,
    force_llm: bool | None = None,
) -> tuple[dict[str, Any], str, list[str], dict[str, Any] | None]:
    hints = page_hints or []
    quality = quality_report.get("quality", "poor")
    use_llm = force_llm if force_llm is not None else os.getenv("MIG_USE_LLM_NORMALIZATION", "1") == "1"
    strict_llm = os.getenv("MIG_STRICT_LLM_NORMALIZATION", "0") == "1"

    if use_llm:
        normalized, llm_artifact = _llm_normalize_document(
            raw_text=raw_text,
            source_file=source_file,
            quality_report=quality_report,
            page_hints=hints,
            strict_llm=strict_llm,
        )
        if strict_llm:
            llm_used = bool(llm_artifact.get("llm_used"))
            parse_fallback_used = bool(llm_artifact.get("parse_fallback_used"))
            if (not llm_used) or parse_fallback_used:
                raise RuntimeError(
                    "Strict LLM normalization is enabled and non-LLM fallback was detected."
                )
        if source_map_overrides:
            normalized.setdefault("source_map", {}).update(source_map_overrides)
        return normalized, "llm-based", quality_report.get("reasons", []), llm_artifact

    if strict_llm:
        raise RuntimeError(
            "Strict LLM normalization is enabled but MIG_USE_LLM_NORMALIZATION is disabled."
        )

    if quality == "good":
        parsed = parse_studio_document(raw_text, source_file=source_file)
        normalized = build_normalized_input(parsed, source_file=source_file)
        normalized.setdefault("source_map", {})["normalization_mode"] = "rule-based"
        if source_map_overrides:
            normalized["source_map"].update(source_map_overrides)
        return normalized, "rule-based", quality_report.get("reasons", []), None

    normalized = _fallback_normalize_document(
        raw_text=raw_text,
        source_file=source_file,
        quality_report=quality_report,
        page_hints=hints,
    )
    if source_map_overrides:
        normalized.setdefault("source_map", {}).update(source_map_overrides)
    return normalized, "hybrid-fallback", quality_report.get("reasons", []), None
