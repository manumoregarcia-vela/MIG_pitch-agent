from __future__ import annotations

import argparse
from pathlib import Path

from agents import QAAgent


def main() -> None:
    parser = argparse.ArgumentParser(description="Run QA evaluation on a pitch deck markdown file.")
    parser.add_argument("--deck", default="draft_deck.md", help="Path to draft deck markdown")
    parser.add_argument("--out", default="qa_report.md", help="Output markdown report path")
    args = parser.parse_args()

    deck_path = Path(args.deck)
    if not deck_path.exists():
        raise FileNotFoundError(f"Deck file not found: {deck_path}")

    qa = QAAgent()
    result = qa.evaluate(deck_path.read_text(encoding="utf-8"))
    report = qa.to_markdown(result)

    out_path = Path(args.out)
    out_path.write_text(report, encoding="utf-8")
    print(f"QA report generated at {out_path}")


if __name__ == "__main__":
    main()
