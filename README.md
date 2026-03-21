# MIG_pitch-agent

Sistema de agentes para crear y mejorar un pitch de videojuego para publishers e inversores.

## Nueva capacidad: Refinement Loop

El pipeline ahora incluye un bucle de refinamiento automático:

1. **Initial pitch**
   - Genera `pitch_strategy`, `slides_outline.json` y `draft_deck.md`.
2. **QA analysis**
   - `qa_agent` detecta debilidades del pitch inicial.
3. **Improved pitch version**
   - Si hay debilidades, el sistema:
     - ajusta `pitch_strategy`
     - regenera `slides_outline.json`
     - regenera `draft_deck.md`

## Outputs

Tras ejecutar el pipeline se producen ambas versiones:

- `outputs/initial_version/`
  - `pitch_strategy.json`
  - `slides_outline.json`
  - `draft_deck.md`
  - `qa_report.json`
- `outputs/improved_version/` (si QA encuentra debilidades)
  - `pitch_strategy.json`
  - `slides_outline.json`
  - `draft_deck.md`
  - `qa_report.json`
- `outputs/run_result.json`

## Ejecutar

```bash
python app.py
```

Mensaje esperado:

```text
Generated initial_version and improved_version outputs in ./outputs
```
