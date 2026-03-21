# MIG_pitch-agent

Demo Day-oriented pitch strategy generator for game studios.

## What changed in this refactor
- `pitch_strategist_agent` logic is now opinionated for top-tier publisher/investor review.
- Explicit 1-5 scoring for: `product`, `traction`, `market`, `business_model`, `team`, `ask`.
- Default audience is `mixed` and narrative is adapted for publisher + investor interest.
- Slide prioritization enforces a 5-8 slide plan centered on gameplay clarity, traction, differentiation, and execution credibility.
- Weakness detection adds compensation narratives to avoid low-confidence pitches.
- `pitch_strategy.md` output now includes scoring breakdown, narrative angle, key selling points, risks, and positioning.

## Files
- `agents.py`: strategist logic + markdown renderer.
- `app.py`: CLI pipeline that reads a studio input and writes `pitch_strategy.md` plus JSON.
- `schemas.json`: output schema for strategy validation.
- `examples/studio_input.json`: executable sample input.

## Usage
```bash
python app.py --input examples/studio_input.json --output pitch_strategy.md --audience mixed
```

Options for `--audience`:
- `mixed` (default)
- `publisher-first`
- `investor-first`

## Output
- `pitch_strategy.md`
- `pitch_strategy.json`

Both are generated from the same strategy object.
