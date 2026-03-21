from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from agents.document_ingestion_agent import ingest_document_to_studio_input, load_studio_input_json
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


def _load_studio_input(mode: str, input_path: str | None) -> dict[str, Any]:
    if mode == "json":
        if input_path:
            return load_studio_input_json(input_path)
        return load_mock_studio_input()

    if mode == "document":
        if not input_path:
            raise ValueError("document mode requires --input pointing to a PDF or DOCX file")
        return ingest_document_to_studio_input(input_path)

    raise ValueError(f"Unsupported mode: {mode}")


def run(mode: str = "json", input_path: str | None = None) -> None:
    outputs_dir = Path("outputs")
    outputs_dir.mkdir(parents=True, exist_ok=True)

    studio_input = _load_studio_input(mode=mode, input_path=input_path)
    summary = build_structured_summary(studio_input)
    strategy = recommend_strategy(summary)
    outline = build_slides_outline(summary, strategy)
    draft_deck = build_draft_deck(summary, strategy, outline)
    qa_report = generate_qa_report(summary, strategy, outline)

    _write_json(outputs_dir / "studio_input.normalized.json", studio_input)
    _write_json(outputs_dir / "structured_summary.json", summary)
    _write_json(outputs_dir / "pitch_strategy.json", strategy)
    _write_json(outputs_dir / "slides_outline.json", {"slides": outline})

    (outputs_dir / "pitch_strategy.md").write_text(_build_strategy_markdown(strategy), encoding="utf-8")
    (outputs_dir / "draft_deck.md").write_text(draft_deck, encoding="utf-8")
    (outputs_dir / "qa_report.md").write_text(qa_report, encoding="utf-8")


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run pitch pipeline with JSON or document ingestion.")
    parser.add_argument(
        "--mode",
        choices=["json", "document"],
        default="json",
        help="Input mode: 'json' for structured JSON, 'document' for PDF/DOCX ingestion.",
    )
    parser.add_argument(
        "--input",
        default=None,
        help="Path to input file. JSON for --mode json; PDF/DOCX for --mode document.",
    )
    return parser


if __name__ == "__main__":
    args = _build_arg_parser().parse_args()
    run(mode=args.mode, input_path=args.input)
