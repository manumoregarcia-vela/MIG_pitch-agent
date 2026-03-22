from __future__ import annotations

import json
import os
from typing import Any

DEFAULT_MODEL = os.getenv("MIG_LLM_MODEL", "gpt-4.1-mini")
DEFAULT_PROVIDER = os.getenv("MIG_LLM_PROVIDER", "openai")
MAX_INPUT_CHARS = int(os.getenv("MIG_LLM_MAX_INPUT_CHARS", "12000"))


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


def _build_prompt(raw_text: str, source_file: str) -> str:
    compact_text = raw_text[:MAX_INPUT_CHARS].strip()
    schema = {
        "studio_profile": {"studio_name": ""},
        "game_profile": {
            "game_name": "",
            "genre": "",
            "platforms": [],
            "development_stage": "",
            "core_fantasy": "",
        },
        "traction": {
            "wishlist": None,
            "retention_d30": None,
            "revenue": None,
            "community_size": None,
        },
        "business": {
            "business_model": "",
            "target_audience": "",
            "current_ask": "",
            "funding_status": "",
        },
        "team": [{"name": "", "role": ""}],
        "assets": {"links": [], "demo": False, "trailer": False},
        "known_gaps": [],
        "source_map": {
            "document": source_file,
            "extraction_notes": [],
        },
    }

    example_input = """Acme Games is building STARFORGE, a co-op survival crafting game for PC and PS5. We have 45,000 Steam wishlists and a playable demo. Team: Ana Perez - CEO, Tom Lee - CTO. Asking for $1.2M seed extension."""
    example_output = {
        "studio_profile": {"studio_name": "Acme Games"},
        "game_profile": {
            "game_name": "STARFORGE",
            "genre": "co-op survival crafting",
            "platforms": ["PC", "PS5"],
            "development_stage": "playable demo",
            "core_fantasy": "",
        },
        "traction": {
            "wishlist": 45000,
            "retention_d30": None,
            "revenue": None,
            "community_size": None,
        },
        "business": {
            "business_model": "",
            "target_audience": "",
            "current_ask": "$1.2M seed extension",
            "funding_status": "",
        },
        "team": [
            {"name": "Ana Perez", "role": "CEO"},
            {"name": "Tom Lee", "role": "CTO"},
        ],
        "assets": {"links": [], "demo": True, "trailer": False},
        "known_gaps": [
            "Missing business.target_audience",
            "Missing business.funding_status",
        ],
        "source_map": {
            "document": "example.txt",
            "extraction_notes": ["platforms inferred from explicit mentions"],
        },
    }

    return (
        "You are an information extraction engine for game-studio pitch documents.\n"
        "Return ONLY valid JSON (no markdown, no explanation).\n"
        "Required top-level keys: studio_profile, game_profile, traction, business, team, assets, known_gaps, source_map.\n"
        "Schema template (match this structure):\n"
        f"{json.dumps(schema, ensure_ascii=False, indent=2)}\n\n"
        "Strict extraction rules:\n"
        "1) Do NOT invent values.\n"
        "2) Extract only explicit or strongly implied information.\n"
        "3) Leave uncertain scalar values as empty string \"\" or null (for numeric metrics).\n"
        "4) Leave uncertain arrays/objects empty.\n"
        "5) Add one known_gaps item for each materially missing section/field needed for an investor pitch.\n"
        "6) source_map.document must be the provided source filename.\n"
        "7) Keep formatting compact and machine-parseable JSON.\n\n"
        "Example input:\n"
        f"{example_input}\n\n"
        "Example output:\n"
        f"{json.dumps(example_output, ensure_ascii=False, indent=2)}\n\n"
        f"Source file: {source_file}\n"
        "Input text to extract from:\n"
        f"{compact_text}"
    )


def _parse_json_payload(payload: str) -> dict[str, Any] | None:
    cleaned = payload.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.replace("json\n", "", 1).strip()

    try:
        data = json.loads(cleaned)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass
    return None


def _coerce_schema(data: dict[str, Any], source_file: str) -> dict[str, Any]:
    normalized = _empty_normalized_template(source_file=source_file, mode="llm-based")

    for key in ["studio_profile", "game_profile", "traction", "business", "assets", "source_map"]:
        value = data.get(key)
        if isinstance(value, dict):
            normalized[key].update(value)

    team = data.get("team")
    if isinstance(team, list):
        normalized["team"] = [member for member in team if isinstance(member, dict)]

    known_gaps = data.get("known_gaps")
    if isinstance(known_gaps, list):
        normalized["known_gaps"] = [str(item) for item in known_gaps if str(item).strip()]

    return normalized


def normalize_text_to_structured_input(raw_text: str, source_file: str) -> tuple[dict[str, Any], dict[str, Any]]:
    if DEFAULT_PROVIDER != "openai":
        raise RuntimeError(f"Unsupported MIG_LLM_PROVIDER: {DEFAULT_PROVIDER}")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is missing; cannot run real LLM normalization.")

    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    prompt = _build_prompt(raw_text=raw_text, source_file=source_file)

    response = client.responses.create(
        model=DEFAULT_MODEL,
        input=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": "Extract structured JSON exactly as requested.",
                    }
                ],
            },
            {
                "role": "user",
                "content": [{"type": "input_text", "text": prompt}],
            },
        ],
        temperature=0,
    )

    parsed = _parse_json_payload(response.output_text)
    parse_fallback_used = False
    if parsed is None:
        parse_fallback_used = True
        parsed = _empty_normalized_template(source_file=source_file, mode="llm-based")
        parsed["known_gaps"].append("Malformed LLM JSON response; used safe empty template")

    normalized = _coerce_schema(parsed, source_file=source_file)
    normalized.setdefault("source_map", {})
    normalized["source_map"].update(
        {
            "normalization_mode": "llm-based",
            "llm_used": True,
            "llm_provider": DEFAULT_PROVIDER,
            "llm_model": DEFAULT_MODEL,
        }
    )

    usage = getattr(response, "usage", None)
    llm_artifact = {
        "mode": "llm-based",
        "provider": DEFAULT_PROVIDER,
        "model": DEFAULT_MODEL,
        "llm_used": True,
        "parse_fallback_used": parse_fallback_used,
        "tokens": {
            "input_tokens": getattr(usage, "input_tokens", None) if usage else None,
            "output_tokens": getattr(usage, "output_tokens", None) if usage else None,
            "total_tokens": getattr(usage, "total_tokens", None) if usage else None,
        },
        "source_file": source_file,
        "input_characters": min(len(raw_text), MAX_INPUT_CHARS),
        "extraction_confidence": None,
        "normalized_output": normalized,
    }
    return normalized, llm_artifact
