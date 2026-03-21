from __future__ import annotations

import argparse
import json
from pathlib import Path

from agents import generate_pitch_strategy


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Demo Day-oriented pitch_strategy.md")
    parser.add_argument("--input", type=Path, default=Path("examples/studio_input.json"))
    parser.add_argument("--output", type=Path, default=Path("pitch_strategy.md"))
    parser.add_argument("--audience", type=str, default="mixed", choices=["mixed", "publisher-first", "investor-first"])
    args = parser.parse_args()

    studio_data = json.loads(args.input.read_text(encoding="utf-8"))
    strategy, md = generate_pitch_strategy(studio_data, audience=args.audience)

    args.output.write_text(md, encoding="utf-8")

    strategy_json_path = args.output.with_suffix(".json")
    strategy_json_path.write_text(json.dumps(strategy, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Generated: {args.output}")
    print(f"Generated: {strategy_json_path}")


if __name__ == "__main__":
    main()
