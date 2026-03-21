from __future__ import annotations

import json
from pathlib import Path

from agents.ingestion_agent import load_mock_studio_input
from agents.pitch_strategist_agent import build_structured_summary, recommend_strategy
from agents.qa_agent import generate_qa_report
from agents.slide_writer_agent import build_draft_deck, build_slides_outline


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def run() -> None:
    output_dir = Path("outputs")
    output_dir.mkdir(parents=True, exist_ok=True)

    mock_input = load_mock_studio_input()
    summary = build_structured_summary(mock_input)
    strategy = recommend_strategy(summary)
    outline = build_slides_outline(summary, strategy)
    draft_deck = build_draft_deck(summary, strategy, outline)
    qa_report = generate_qa_report(summary, outline)

    _write_json(output_dir / "structured_summary.json", summary)

    strategy_md = [
        "# Pitch Strategy",
        "",
        f"## Audience principal\n{strategy['audience_type']}",
        "",
        "## Recomendación narrativa",
        strategy["narrative_recommendation"],
        "",
        "## Mensajes prioritarios",
        *[f"- {message}" for message in strategy["priority_messages"]],
        "",
        "## Riesgos o debilidades a compensar",
        *[f"- {risk}" for risk in strategy["risks_to_compensate"]],
        "",
        "## Orden recomendado de slides",
        *[f"{idx + 1}. {slide}" for idx, slide in enumerate(strategy["recommended_slide_order"])],
    ]
    (output_dir / "pitch_strategy.md").write_text("\n".join(strategy_md), encoding="utf-8")

    _write_json(output_dir / "slides_outline.json", {"slides": outline})
    (output_dir / "draft_deck.md").write_text(draft_deck, encoding="utf-8")
    (output_dir / "qa_report.md").write_text(qa_report, encoding="utf-8")


if __name__ == "__main__":
    run()
