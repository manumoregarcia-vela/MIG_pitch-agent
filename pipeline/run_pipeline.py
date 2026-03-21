from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from agents.document_ingestion_agent import (
    build_normalized_input,
    extract_text_from_document,
    list_supported_documents,
    load_studio_input_json,
    parse_studio_document,
)
from agents.ingestion_agent import load_mock_studio_input
from agents.pitch_strategist_agent import build_structured_summary, recommend_strategy
from agents.qa_agent import generate_qa_report
from agents.slide_writer_agent import build_draft_deck, build_slides_outline


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _build_strategy_markdown(strategy: dict[str, Any]) -> str:
    lines = [
        "# Pitch Strategy",
        "",
        f"## Audience\n{strategy['audience_type']}",
        "",
        "## Narrative recommendation",
        strategy["narrative_recommendation"],
        "",
        "## Priority messages",
        *[f"- {message}" for message in strategy["priority_messages"]],
        "",
        "## Risks to compensate",
        *[f"- {risk}" for risk in strategy["risks_to_compensate"]],
        "",
        "## Recommended slide order",
        *[f"{index}. {slide}" for index, slide in enumerate(strategy["recommended_slide_order"], start=1)],
    ]
    return "\n".join(lines)


def _select_document_from_data(data_dir: Path) -> Path:
    docs = list_supported_documents(data_dir)
    if not docs:
        raise FileNotFoundError(
            f"No supported documents found in '{data_dir}'. Supported types: .pdf, .docx, .txt"
        )

    selected = docs[0]
    if len(docs) > 1:
        print(f"[document-mode] Multiple files found. Selected '{selected.name}' (sorted order).")
    else:
        print(f"[document-mode] Selected '{selected.name}'.")

    return selected


def _load_studio_input(
    mode: str,
    input_path: str | None,
    outputs_dir: Path,
    data_dir: Path,
) -> tuple[dict[str, Any], str | None]:
    if mode == "json":
        if input_path:
            return load_studio_input_json(input_path), None
        return load_mock_studio_input(), None

    if mode == "document":
        selected = Path(input_path) if input_path else _select_document_from_data(data_dir)
        if not selected.exists() or not selected.is_file():
            raise FileNotFoundError(f"Input document not found: {selected}")

        raw_text = extract_text_from_document(selected)
        (outputs_dir / "raw_extracted_text.txt").write_text(raw_text, encoding="utf-8")

        parsed = parse_studio_document(raw_text, source_file=selected.name)
        studio_input = build_normalized_input(parsed, source_file=selected.name)
        _write_json(outputs_dir / "normalized_input.json", studio_input)

        return studio_input, selected.name

    raise ValueError(f"Unsupported mode: {mode}")


def run(mode: str = "json", input_path: str | None = None, data_dir: str = "data") -> None:
    outputs_dir = Path("outputs")
    outputs_dir.mkdir(parents=True, exist_ok=True)

    studio_input, selected_document = _load_studio_input(
        mode=mode,
        input_path=input_path,
        outputs_dir=outputs_dir,
        data_dir=Path(data_dir),
    )

    summary = build_structured_summary(studio_input)
    strategy = recommend_strategy(summary)
    outline = build_slides_outline(summary, strategy)
    draft_deck = build_draft_deck(summary, strategy, outline)
    qa_report = generate_qa_report(summary, strategy, outline)

    _write_json(outputs_dir / "structured_summary.json", summary)
    _write_json(outputs_dir / "pitch_strategy.json", strategy)
    _write_json(outputs_dir / "slides_outline.json", {"slides": outline})

    (outputs_dir / "pitch_strategy.md").write_text(_build_strategy_markdown(strategy), encoding="utf-8")
    (outputs_dir / "draft_deck.md").write_text(draft_deck, encoding="utf-8")
    (outputs_dir / "qa_report.md").write_text(qa_report, encoding="utf-8")

    if mode == "json":
        _write_json(outputs_dir / "normalized_input.json", studio_input)
    if selected_document:
        print(f"[document-mode] Pipeline completed using: {selected_document}")


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run pitch pipeline with JSON or document ingestion.")
    parser.add_argument(
        "--mode",
        choices=["json", "document"],
        default="document",
        help="Input mode: 'json' for structured JSON, 'document' for /data document ingestion.",
    )
    parser.add_argument(
        "--input",
        default=None,
        help="Optional path override. JSON for --mode json; document file for --mode document.",
    )
    parser.add_argument(
        "--data-dir",
        default="data",
        help="Directory inspected in document mode when --input is not provided.",
    )
    return parser


if __name__ == "__main__":
    args = _build_arg_parser().parse_args()
    run(mode=args.mode, input_path=args.input, data_dir=args.data_dir)
