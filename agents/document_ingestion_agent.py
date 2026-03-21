from __future__ import annotations

import json
import re
import subprocess
import zipfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}


PDF_NOISE_PATTERNS = [
    r"\b\d+\s+\d+\s+obj\b",
    r"\bendobj\b",
    r"\bstream\b",
    r"\bendstream\b",
    r"/Type\s*/Page",
    r"/XObject",
    r"FlateDecode",
    r"BitsPerComponent",
    r"ColorSpace",
    r"Length\s+\d+",
]


def list_supported_documents(data_dir: Path) -> list[Path]:
    """Return supported document files inside data_dir, sorted by name."""
    if not data_dir.exists() or not data_dir.is_dir():
        return []

    files = [
        path
        for path in data_dir.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    ]
    return sorted(files, key=lambda p: p.name.lower())


def _clean_pdf_extracted_text(text: str) -> str:
    cleaned = text
    for pattern in PDF_NOISE_PATTERNS:
        cleaned = re.sub(pattern, " ", cleaned, flags=re.IGNORECASE)

    lines = []
    for raw_line in cleaned.splitlines():
        line = re.sub(r"\s+", " ", raw_line).strip()
        if not line:
            continue
        if line.startswith(("/", "<<", ">>")) and len(line.split()) < 8:
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def extract_text_from_pdf(path: Path) -> str:
    """Extract text from a PDF file using pypdf, falling back to pdftotext."""
    try:
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        chunks: list[str] = []
        for idx, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            text = _clean_pdf_extracted_text(text)
            if text:
                chunks.append(f"[PAGE {idx}]\n{text}")
        return "\n\n".join(chunks).strip()
    except ImportError:
        pass

    try:
        result = subprocess.run(
            ["pdftotext", str(path), "-"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            return _clean_pdf_extracted_text(result.stdout.strip())
    except FileNotFoundError:
        pass

    raw_bytes = path.read_bytes()
    ascii_runs = re.findall(rb"[A-Za-z0-9][A-Za-z0-9 ,.:;_/\-()]{8,}", raw_bytes)
    decoded_chunks = [chunk.decode("latin-1", errors="ignore").strip() for chunk in ascii_runs]
    filtered = [
        chunk
        for chunk in decoded_chunks
        if not chunk.startswith(("obj", "endobj", "stream", "endstream", "/")) and len(chunk) > 8
    ]
    fallback_text = _clean_pdf_extracted_text("\n".join(filtered))
    if fallback_text:
        return fallback_text

    raise RuntimeError("Could not extract PDF text. Install 'pypdf' for robust PDF ingestion.")


def extract_text_from_docx(path: Path) -> str:
    """Extract text from a DOCX file using python-docx, with stdlib fallback."""
    try:
        import docx

        document = docx.Document(str(path))
        lines = [paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip()]
        return "\n".join(lines).strip()
    except ImportError:
        pass

    with zipfile.ZipFile(path) as archive:
        xml_data = archive.read("word/document.xml")
    root = ElementTree.fromstring(xml_data)
    paragraphs: list[str] = []
    for paragraph in root.findall(".//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p"):
        text_nodes = paragraph.findall(".//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t")
        text = "".join(node.text or "" for node in text_nodes).strip()
        if text:
            paragraphs.append(text)
    return "\n".join(paragraphs).strip()


def extract_text_from_txt(path: Path) -> str:
    """Extract text from plain TXT files."""
    return path.read_text(encoding="utf-8", errors="ignore").strip()


def extract_text_from_document(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return extract_text_from_pdf(path)
    if suffix == ".docx":
        return extract_text_from_docx(path)
    if suffix == ".txt":
        return extract_text_from_txt(path)
    raise ValueError(f"Unsupported file type: {path.suffix}")


def extract_document_with_hints(path: Path) -> dict[str, Any]:
    raw_text = extract_text_from_document(path)

    page_hints: list[dict[str, Any]] = []
    page_chunks = re.split(r"\[PAGE\s+(\d+)\]", raw_text)
    if len(page_chunks) > 1:
        for i in range(1, len(page_chunks), 2):
            page_num = int(page_chunks[i])
            page_text = page_chunks[i + 1].strip() if i + 1 < len(page_chunks) else ""
            sample = " ".join(page_text.split())[:240]
            page_hints.append(
                {
                    "page": page_num,
                    "char_count": len(page_text),
                    "word_count": len(re.findall(r"[A-Za-z][A-Za-z\-']{2,}", page_text)),
                    "sample_text": sample,
                }
            )

    return {
        "raw_text": raw_text,
        "page_hints": page_hints,
        "source_file": path.name,
    }


def _find_first(raw_text: str, patterns: list[str]) -> str:
    for pattern in patterns:
        match = re.search(pattern, raw_text, flags=re.IGNORECASE | re.MULTILINE)
        if match:
            value = match.group(1).strip(" .:-\n\t")
            if value:
                return value
    return ""


def _parse_platforms(raw_text: str) -> list[str]:
    known = [
        "PC",
        "Steam",
        "PlayStation 5",
        "PS5",
        "PlayStation 4",
        "PS4",
        "Xbox Series X",
        "Xbox",
        "Nintendo Switch",
        "Switch",
        "iOS",
        "Android",
        "Mobile",
    ]
    found: list[str] = []
    lowered = raw_text.lower()
    for platform in known:
        if platform.lower() in lowered:
            label = "PC" if platform == "Steam" else platform
            if label not in found:
                found.append(label)

    line = _find_first(raw_text, [r"platforms?\s*[:\-]\s*([^\n]+)"])
    if line:
        for item in re.split(r"[,/|]", line):
            value = item.strip()
            if value and value not in found:
                found.append(value)

    return found


def _extract_metric(raw_text: str, label_patterns: list[str]) -> int | None:
    num_group = r"([\d\.,\s]+(?:k|m)?)"
    for label in label_patterns:
        match = re.search(rf"{label}[^\d]{{0,20}}{num_group}", raw_text, flags=re.IGNORECASE)
        if not match:
            continue
        value = match.group(1).strip().lower().replace(" ", "")
        multiplier = 1
        if value.endswith("k"):
            multiplier = 1_000
            value = value[:-1]
        elif value.endswith("m"):
            multiplier = 1_000_000
            value = value[:-1]
        cleaned = re.sub(r"[^\d]", "", value)
        if cleaned:
            return int(cleaned) * multiplier
    return None


def _extract_assets(raw_text: str) -> dict[str, Any]:
    assets: dict[str, Any] = {}
    lowered = raw_text.lower()

    asset_keywords = {
        "video": ["video", "trailer", "youtube", "vimeo"],
        "gameplay": ["gameplay"],
        "demo": ["demo"],
        "screenshots": ["screenshot", "screenshots"],
        "press_kit": ["press kit", "presskit"],
        "steam_page": ["steam page", "store.steampowered.com"],
    }

    for key, keywords in asset_keywords.items():
        if any(keyword in lowered for keyword in keywords):
            assets[key] = True

    url_matches = re.findall(r"https?://\S+", raw_text)
    if url_matches:
        assets["links"] = [url.rstrip(").,;") for url in url_matches]

    return assets


def _extract_team(raw_text: str) -> dict[str, Any]:
    team_count = _extract_metric(raw_text, [r"team\s*size", r"team\s*of", r"\bwe are\b"])
    member_lines: list[dict[str, str]] = []

    for match in re.finditer(
        r"^[-•]\s*([A-Z][A-Za-z\-\s']{2,})\s*[\-:–]\s*([^\n]{3,120})$",
        raw_text,
        flags=re.MULTILINE,
    ):
        name = match.group(1).strip()
        role = match.group(2).strip()
        member_lines.append({"name": name, "role": role})

    result: dict[str, Any] = {}
    if team_count:
        result["team_size"] = team_count
    if member_lines:
        result["members"] = member_lines
    return result


def parse_studio_document(raw_text: str, source_file: str) -> dict[str, Any]:
    text = raw_text.strip()

    parsed: dict[str, Any] = {
        "studio_name": _find_first(
            text,
            [
                r"studio\s*name\s*[:\-]\s*([^\n]+)",
                r"company\s*name\s*[:\-]\s*([^\n]+)",
                r"^([A-Z][\w\s&\-]{2,60}(?:studio|games|interactive))$",
            ],
        ),
        "game_name": _find_first(
            text,
            [
                r"game\s*name\s*[:\-]\s*([^\n]+)",
                r"title\s*[:\-]\s*([^\n]+)",
                r"project\s*[:\-]\s*([^\n]+)",
            ],
        ),
        "genre": _find_first(text, [r"genre\s*[:\-]\s*([^\n]+)"]),
        "platforms": _parse_platforms(text),
        "development_stage": _find_first(
            text,
            [
                r"development\s*stage\s*[:\-]\s*([^\n]+)",
                r"stage\s*[:\-]\s*([^\n]+)",
                r"status\s*[:\-]\s*([^\n]+)",
            ],
        ),
        "core_fantasy": _find_first(
            text,
            [
                r"core\s*fantasy\s*[:\-]\s*([^\n]+)",
                r"game\s*hook\s*[:\-]\s*([^\n]+)",
                r"hook\s*[:\-]\s*([^\n]+)",
                r"elevator\s*pitch\s*[:\-]\s*([^\n]+)",
            ],
        ),
        "business_model": _find_first(text, [r"business\s*model\s*[:\-]\s*([^\n]+)"]),
        "target_audience": _find_first(text, [r"target\s*audience\s*[:\-]\s*([^\n]+)"]),
        "current_ask": _find_first(
            text,
            [
                r"current\s*ask\s*[:\-]\s*([^\n]+)",
                r"ask\s*[:\-]\s*([^\n]+)",
                r"seeking\s*[:\-]\s*([^\n]+)",
            ],
        ),
        "funding_status": _find_first(text, [r"funding\s*status\s*[:\-]\s*([^\n]+)"]),
        "traction": {
            "steam_wishlists": _extract_metric(text, [r"steam\s+wishlists?", r"wishlists?"]),
            "demo_downloads": _extract_metric(text, [r"demo\s+downloads?", r"downloads?"]),
            "trailer_views": _extract_metric(text, [r"trailer\s+views?", r"views?"]),
            "community_size": _extract_metric(
                text,
                [r"community\s+size", r"discord\s+members?", r"followers?", r"newsletter\s+subscribers?"],
            ),
        },
        "team": _extract_team(text),
        "assets": _extract_assets(text),
        "source_file": source_file,
    }

    return parsed


def build_normalized_input(parsed_content: dict[str, Any], source_file: str) -> dict[str, Any]:
    traction_clean = {
        key: value
        for key, value in parsed_content.get("traction", {}).items()
        if value is not None
    }

    team_section: list[dict[str, Any]] = parsed_content.get("team", {}).get("members", [])
    studio_profile = {"studio_name": parsed_content.get("studio_name", "")}
    team_size = parsed_content.get("team", {}).get("team_size")
    if team_size:
        studio_profile["team_size"] = team_size

    normalized = {
        "studio_profile": studio_profile,
        "game_profile": {
            "game_name": parsed_content.get("game_name", ""),
            "genre": parsed_content.get("genre", ""),
            "platforms": parsed_content.get("platforms", []),
            "development_stage": parsed_content.get("development_stage", ""),
            "core_fantasy": parsed_content.get("core_fantasy", ""),
        },
        "traction": traction_clean,
        "business": {
            "business_model": parsed_content.get("business_model", ""),
            "target_audience": parsed_content.get("target_audience", ""),
            "current_ask": parsed_content.get("current_ask", ""),
            "funding_status": parsed_content.get("funding_status", ""),
        },
        "team": team_section,
        "assets": parsed_content.get("assets", {}),
        "known_gaps": [],
        "source_map": {
            "document": source_file,
            "ingestion": "rule-based parser",
        },
    }

    required_fields = {
        "studio_profile.studio_name": normalized["studio_profile"].get("studio_name"),
        "game_profile.game_name": normalized["game_profile"].get("game_name"),
        "game_profile.genre": normalized["game_profile"].get("genre"),
        "game_profile.platforms": normalized["game_profile"].get("platforms"),
        "game_profile.development_stage": normalized["game_profile"].get("development_stage"),
        "game_profile.core_fantasy": normalized["game_profile"].get("core_fantasy"),
        "business.business_model": normalized["business"].get("business_model"),
        "business.target_audience": normalized["business"].get("target_audience"),
        "business.current_ask": normalized["business"].get("current_ask"),
        "business.funding_status": normalized["business"].get("funding_status"),
        "traction.steam_wishlists": normalized["traction"].get("steam_wishlists"),
        "traction.demo_downloads": normalized["traction"].get("demo_downloads"),
        "traction.trailer_views": normalized["traction"].get("trailer_views"),
        "traction.community_size": normalized["traction"].get("community_size"),
    }

    for field, value in required_fields.items():
        if value in (None, "", []):
            normalized["known_gaps"].append(f"Missing: {field}")

    return normalized


def load_studio_input_json(input_path: str) -> dict[str, Any]:
    path = Path(input_path)
    return json.loads(path.read_text(encoding="utf-8"))


def ingest_document_to_studio_input(input_path: str) -> dict[str, Any]:
    path = Path(input_path)
    raw_text = extract_text_from_document(path)
    parsed = parse_studio_document(raw_text, source_file=path.name)
    return build_normalized_input(parsed, source_file=path.name)
