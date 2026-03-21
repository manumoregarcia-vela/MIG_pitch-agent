# MIG_pitch-agent
Sistema de agentes para la revisión y creación de pitch para publishers e inversores.

## Objetivo
Generar automáticamente decks de 5-8 slides optimizados para publishers e inversores.

## Inputs
- Decks
- Web
- Steam
- Redes sociales
- Métricas

## Outputs
- structured_summary.json
- pitch_strategy.md
- slides_outline.json
- draft_deck.md
- pptx
- qa_report.md

## QA Agent (V1)
El `QAAgent` ahora evalúa calidad de pitch y no solo checklist:
- Scoring de calidad: claridad, credibilidad, tracción, diferenciación y appeal inversor/publisher.
- Detección de issues: demasiado genérico, concepto poco claro, métricas débiles, ask no claro y exceso de texto.
- Recomendaciones accionables: qué cambiar, qué quitar y qué enfatizar.
- `Demo Day readiness score` (0-100).

### Ejecutar QA
```bash
python app.py --deck draft_deck.md --out qa_report.md
```

## Estado
V1 en desarrollo con Codex.
