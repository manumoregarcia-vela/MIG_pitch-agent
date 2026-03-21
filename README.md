# MIG_pitch-agent

Demo Day-oriented pitch strategy generator for game studios.

## Overview

Sistema de agentes para generar y optimizar pitches de videojuegos (5-8 slides) orientados a Demo Day, maximizando interés de publishers e inversores.

## Pipeline agents

- `document_ingestion_agent`: extracción y parsing rule-based de documentos reales.
- `ingestion_agent`: mock/json fallback.
- `pitch_strategist_agent`: resumen estructurado + estrategia.
- `slide_writer_agent`: outline + draft deck.
- `qa_agent`: QA del deck recomendado.

## New `/data` document ingestion flow

1. Coloca un archivo fuente en `/data`.
2. Tipos soportados:
   - `.pdf`
   - `.docx`
   - `.txt`
3. Ejecuta el pipeline en modo documento (`--mode document`, default).
4. Selección de archivo en V1:
   - si hay **1** documento válido: se usa automáticamente
   - si hay **varios**: se elige el primero en orden alfabético y se imprime en logs
   - si no hay documentos soportados: se lanza error claro
5. El sistema extrae texto, parsea campos con reglas (sin LLM), normaliza el input y ejecuta el pipeline completo.

## Outputs generated in `/outputs`

- `raw_extracted_text.txt`
- `normalized_input.json`
- `structured_summary.json`
- `pitch_strategy.json`
- `pitch_strategy.md`
- `slides_outline.json`
- `draft_deck.md`
- `qa_report.md`

## Usage

### Run with document ingestion (default)

```bash
python app.py
```

### Run with explicit mode

```bash
python app.py --mode document
```

### Run from a specific file

```bash
python app.py --mode document --input data/your_file.pdf
```

### Run from JSON mode (compatible with previous flow)

```bash
python app.py --mode json --input examples/studio_input_real.json
```

## Notes

- El parser de documentos es V1 rule-based (keywords, regex y heurísticas simples).
- Si un campo no se detecta, se deja vacío y se registra en `known_gaps`.
- No se inventan valores faltantes.
