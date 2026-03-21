from __future__ import annotations

import json
from pathlib import Path

from agents import RefinementLoopOrchestrator


OUTPUT_DIR = Path("outputs")


MOCK_SUMMARY = {
    "studio_name": "Nebula Forge",
    "game_name": "Shardfall",
    "genre": "Action RPG",
    "platform": ["PC", "Console"],
    "development_stage": "Vertical slice",
    "traction_signals": ["15k wishlists", "Playable demo"],
    "current_ask": "Publisher partnership + 1.2M€ co-funding",
}


def write_version_outputs(version_name: str, version_payload: dict) -> None:
    version_dir = OUTPUT_DIR / version_name
    version_dir.mkdir(parents=True, exist_ok=True)

    (version_dir / "pitch_strategy.json").write_text(
        json.dumps(version_payload["pitch_strategy"], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (version_dir / "slides_outline.json").write_text(
        json.dumps(version_payload["slides_outline"], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (version_dir / "draft_deck.md").write_text(
        version_payload["draft_deck"]["markdown"],
        encoding="utf-8",
    )
    (version_dir / "qa_report.json").write_text(
        json.dumps(version_payload["qa_report"], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def main() -> None:
    orchestrator = RefinementLoopOrchestrator()
    run_output = orchestrator.run(MOCK_SUMMARY)

    OUTPUT_DIR.mkdir(exist_ok=True)
    write_version_outputs("initial_version", run_output["initial_version"])

    if run_output["improved_version"] is not None:
        write_version_outputs("improved_version", run_output["improved_version"])

    (OUTPUT_DIR / "run_result.json").write_text(
        json.dumps(run_output, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("Generated initial_version and improved_version outputs in ./outputs")


if __name__ == "__main__":
    main()
