from __future__ import annotations

import json
import re
import zipfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

SECTION_KEYS = [
    "studio_profile",
    "game_profile",
    "traction",
    "business",
    "team",
    "assets",
    "known_gaps",
    "source_map",
]

MISSING_CRITICAL_FIELD_HINTS = {
    "studio_profile": ["studio_name"],
    "game_profile": ["game_name", "genre", "development_stage"],
    "traction": ["steam_wishlists", "demo_downloads"],
    "business": ["business_model", "current_ask"],
    "team": ["at_least_one_member"],
}


def _normalize_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _normalize_document_text(value: str) -> str:
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


def read_pdf_text(path: Path) -> str:
    """Extract raw text from a PDF file using available local libraries."""
    try:
        from pypdf import PdfReader  # type: ignore

        reader = PdfReader(str(path))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    except Exception:
        pass

    try:
        from PyPDF2 import PdfReader  # type: ignore

        reader = PdfReader(str(path))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    except Exception as exc:
        raise RuntimeError(
            "Could not read PDF. Install 'pypdf' (recommended) or 'PyPDF2'."
        ) from exc


def read_docx_text(path: Path) -> str:
    """Extract raw text from a DOCX file without external dependencies."""
    with zipfile.ZipFile(path) as zipped:
        xml_content = zipped.read("word/document.xml")

    root = ElementTree.fromstring(xml_content)
    text_nodes = []
    for node in root.iter():
        if node.tag.endswith("}t") and node.text:
            text_nodes.append(node.text)

    return "\n".join(text_nodes)


def read_document_text(document_path: str | Path) -> str:
    path = Path(document_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return _normalize_document_text(read_pdf_text(path))
    if suffix == ".docx":
        return _normalize_document_text(read_docx_text(path))

    raise ValueError(f"Unsupported document type: {suffix}. Use PDF or DOCX.")


def _extract_int_near(label_patterns: list[str], text: str) -> int | None:
    for pattern in label_patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            raw = match.group(1).replace(",", "")
            if raw.isdigit():
                return int(raw)
    return None


def _extract_text_near(label_patterns: list[str], text: str) -> str | None:
    for pattern in label_patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            value = _normalize_whitespace(match.group(1))
            if value:
                return value
    return None


def _extract_urls(text: str) -> list[str]:
    return re.findall(r"https?://[^\s)\]>]+", text)


def parse_text_to_studio_input(raw_text: str, source_name: str) -> dict[str, Any]:
    """Best-effort parser for V1 document ingestion.

    The parser is intentionally conservative: unknown values are left empty and
    tracked under known_gaps/missing_critical_info instead of being invented.
    """
    text = raw_text

    studio_name = _extract_text_near([
        r"studio\s*name\s*[:\-]\s*([^\n\.]{2,120})",
        r"company\s*[:\-]\s*([^\n\.]{2,120})",
    ], text)
    game_name = _extract_text_near([
        r"game\s*name\s*[:\-]\s*([^\n\.]{2,120})",
        r"title\s*[:\-]\s*([^\n\.]{2,120})",
    ], text)
    genre = _extract_text_near([r"genre\s*[:\-]\s*([^\n\.]{2,120})"], text)
    development_stage = _extract_text_near([
        r"development\s*stage\s*[:\-]\s*([^\n\.]{2,160})",
        r"stage\s*[:\-]\s*([^\n\.]{2,160})",
    ], text)
    core_fantasy = _extract_text_near([
        r"(core\s*fantasy|usp|unique\s*selling\s*point)\s*[:\-]\s*([^\n]{5,240})"
    ], text)
    if core_fantasy:
        two_group = re.search(r"(core\s*fantasy|usp|unique\s*selling\s*point)\s*[:\-]\s*([^\n]{5,240})", text, flags=re.IGNORECASE)
        if two_group:
            core_fantasy = _normalize_whitespace(two_group.group(2))

    business_model = _extract_text_near([r"business\s*model\s*[:\-]\s*([^\n]{2,240})"], text)
    target_audience = _extract_text_near([r"(target\s*audience|audience)\s*[:\-]\s*([^\n]{2,240})"], text)
    if target_audience:
        ta = re.search(r"(target\s*audience|audience)\s*[:\-]\s*([^\n]{2,240})", text, flags=re.IGNORECASE)
        if ta:
            target_audience = _normalize_whitespace(ta.group(2))

    current_ask = _extract_text_near([r"(current\s*ask|ask|seeking)\s*[:\-]\s*([^\n]{2,280})"], text)
    if current_ask:
        ask = re.search(r"(current\s*ask|ask|seeking)\s*[:\-]\s*([^\n]{2,280})", text, flags=re.IGNORECASE)
        if ask:
            current_ask = _normalize_whitespace(ask.group(2))

    funding_status = _extract_text_near([r"funding\s*status\s*[:\-]\s*([^\n]{2,180})"], text)

    platforms = []
    if re.search(r"\bpc\b", text, re.IGNORECASE):
        platforms.append("PC")
    if re.search(r"\bplaystation\b|\bps5\b|\bps4\b", text, re.IGNORECASE):
        platforms.append("PlayStation")
    if re.search(r"\bxbox\b", text, re.IGNORECASE):
        platforms.append("Xbox")
    if re.search(r"\bswitch\b|\bnintendo\b", text, re.IGNORECASE):
        platforms.append("Nintendo Switch")
    if re.search(r"\bmobile\b|\bios\b|\bandroid\b", text, re.IGNORECASE):
        platforms.append("Mobile")

    steam_wishlists = _extract_int_near([r"([0-9][0-9,]{2,})\s*steam\s*wishlists"], text)
    demo_downloads = _extract_int_near([
        r"([0-9][0-9,]{2,})\s*demo\s*(downloads|players)",
        r"([0-9][0-9,]{2,})\s*(downloads|players)\s*in\s*demo",
    ], text)
    discord_members = _extract_int_near([r"([0-9][0-9,]{2,})\s*discord\s*(members|community)?"], text)
    trailer_views = _extract_int_near([
        r"([0-9][0-9,]{2,})\s*(youtube\s*)?(trailer\s*)?views",
        r"([0-9][0-9,]{2,})\s*trailer\s*views",
    ], text)

    team_entries: list[dict[str, str]] = []
    blocked_name_tokens = {
        "studio name",
        "game name",
        "development stage",
        "business model",
        "current ask",
        "target audience",
        "funding status",
    }
    for match in re.finditer(r"([A-Z][a-z]+\s+[A-Z][a-z]+)\s*[\-–:]\s*([^\n]{2,120})", raw_text):
        name = _normalize_whitespace(match.group(1))
        role = _normalize_whitespace(match.group(2))
        if name.lower() in blocked_name_tokens:
            continue
        team_entries.append({"name": name, "role": role, "credential": ""})
    # deduplicate while preserving order
    deduped_team = []
    seen = set()
    for member in team_entries:
        key = (member["name"], member["role"])
        if key not in seen:
            deduped_team.append(member)
            seen.add(key)

    urls = _extract_urls(raw_text)
    assets: dict[str, Any] = {}
    for url in urls:
        lower_url = url.lower()
        if "steam" in lower_url and "steam_page" not in assets:
            assets["steam_page"] = url
        elif any(k in lower_url for k in ["youtube", "youtu.be", "vimeo"]) and "gameplay_video" not in assets:
            assets["gameplay_video"] = url
        elif "press" in lower_url and "press_kit" not in assets:
            assets["press_kit"] = url

    studio_input: dict[str, Any] = {
        "studio_profile": {
            "studio_name": studio_name or "",
            "location": "",
            "team_size": len(deduped_team) if deduped_team else None,
            "founded_year": None,
        },
        "game_profile": {
            "game_name": game_name or "",
            "genre": genre or "",
            "platforms": platforms,
            "development_stage": development_stage or "",
            "core_fantasy": core_fantasy or "",
        },
        "traction": {
            "steam_wishlists": steam_wishlists or 0,
            "demo_downloads": demo_downloads or 0,
            "discord_members": discord_members or 0,
            "trailer_views": trailer_views or 0,
        },
        "business": {
            "business_model": business_model or "",
            "target_audience": target_audience or "",
            "current_ask": current_ask or "",
            "funding_status": funding_status or "",
        },
        "team": deduped_team,
        "assets": assets,
        "known_gaps": [],
        "source_map": {
            key: source_name for key in SECTION_KEYS if key != "known_gaps"
        },
    }

    missing_critical_info: list[str] = []

    for section, fields in MISSING_CRITICAL_FIELD_HINTS.items():
        if section == "team":
            if not studio_input["team"]:
                missing_critical_info.append("team: at least one identified team member")
            continue

        section_data = studio_input.get(section, {})
        for field in fields:
            value = section_data.get(field)
            if value in (None, "", 0, []):
                missing_critical_info.append(f"{section}: {field}")

    if not studio_input["assets"]:
        missing_critical_info.append("assets: at least one pitch asset URL")

    studio_input["known_gaps"] = missing_critical_info
    studio_input["missing_critical_info"] = missing_critical_info
    return studio_input


def ingest_document_to_studio_input(document_path: str | Path) -> dict[str, Any]:
    path = Path(document_path)
    raw_text = read_document_text(path)
    parsed = parse_text_to_studio_input(raw_text, source_name=path.name)
    parsed["raw_text"] = raw_text
    return parsed


def load_studio_input_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))
