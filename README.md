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
V1 mínima de un sistema de agentes para generar pitches de videojuegos para Demo Day.

## Qué implementa esta V1
Pipeline end-to-end con input mock hardcodeado que genera:

- `outputs/structured_summary.json`
- `outputs/pitch_strategy.md`
- `outputs/slides_outline.json`
- `outputs/draft_deck.md`
- `outputs/qa_report.md`

Arquitectura implementada:

- `ingestion` (mock)
- `pitch_strategist` (framework de evaluación con separación de hechos/inferencias/missing)
- `slide_writer`
- `qa_agent`

## Estructura de carpetas

- `agents/`: agentes/módulos especializados
- `pipeline/`: orquestación de ejecución
- `outputs/`: artefactos generados
- `app.py`: entrypoint simple

## Cómo ejecutar

Requisitos: Python 3.10+

```bash
python app.py
```

Al ejecutar, se regeneran todos los outputs en la carpeta `outputs/`.

## Principios de calidad aplicados

- No inventar datos: toda la información factual proviene del input mock.
- Separación explícita de:
  - hechos (`facts`)
  - inferencias (`inferences`)
  - datos faltantes (`missing_critical_info`)
- Trazabilidad mediante `source_map`.

## TODOs V2

- TODO: **Research Agent** para enriquecer datos desde fuentes públicas (web/store/social/press).
- TODO: **Validation Agent** para verificar claims y consistencia inter-fuente con scoring de confianza.
- TODO: **PPTX generation** con plantilla base e inserción automática de assets.

## Nota de alcance

Esta versión prioriza simplicidad y claridad del flujo sobre complejidad. Está preparada para ampliar con parsing documental, LLM prompts desacoplados y generación de PPTX en iteraciones siguientes.
