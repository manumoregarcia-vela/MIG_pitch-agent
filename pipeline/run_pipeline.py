from __future__ import annotations

import json
from pathlib import Path
from typing import Any

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


def run() -> None:
    outputs_dir = Path("outputs")
    outputs_dir.mkdir(parents=True, exist_ok=True)

    studio_input = load_mock_studio_input()
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


if __name__ == "__main__":
    run()
