# MIG_pitch-agent

Demo Day-oriented pitch strategy generator for game studios.

## Overview

Sistema de agentes para generar y optimizar pitches de videojuegos (5-8 slides) orientados a Demo Day, maximizando interés de publishers e inversores.

## Pipeline agents

- `document_ingestion_agent`: extracción documental + limpieza + hints por página.
- `document_quality_agent`: evaluación de calidad del texto extraído.
- `document_normalizer_agent`: normalización híbrida (rule-based o fallback).
- `ingestion_agent`: mock/json fallback.
- `pitch_strategist_agent`: resumen estructurado + estrategia.
- `slide_writer_agent`: outline + draft deck.
- `qa_agent`: QA del deck recomendado.

## New `/data` hybrid ingestion flow

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
5. Sidecar text opcional (preferido):
   - para un documento `data/SomeDeck.pdf`, el pipeline busca sidecars en este orden:
     1. `data/SomeDeck.extracted.txt`
     2. `data/SomeDeck.cleaned.md`
     3. `data/SomeDeck.txt`
   - si existe alguno, se usa como `text_source` principal (modo `sidecar-text`) y se evita la extracción raw del PDF/DOCX.
   - si no existe, se mantiene la extracción normal desde el documento original (modo `raw-document`).
6. Extracción y evaluación de calidad:
   - siempre se guarda el texto base en `outputs/raw_extracted_text.txt` (venga de sidecar o de extracción raw).
   - se calcula `outputs/extraction_quality.json`.
7. Normalización condicional:
   - **Rule-based mode** (calidad `good`): parser por reglas/regex directo
   - **Hybrid fallback mode** (calidad `poor`): usa representación compacta (snippets, hints por página, filename, marcadores) y normaliza con path fallback preparado para asistencia LLM
8. `outputs/normalized_input.json` incluye `source_map` enriquecido con:
   - `document`
   - `text_source`
   - `ingestion_mode` (`sidecar-text` o `raw-document`)
   - `sidecar_text_used`
   - `normalization_mode` (`rule-based` o `hybrid-fallback`)

### Why image-based pitch decks need fallback

Muchos pitch decks visuales contienen poco texto seleccionable y mucho contenido rasterizado. En esos casos el extractor PDF devuelve tokens internos (`obj`, `/Page`, `FlateDecode`, etc.) o texto fragmentado. El fallback híbrido evita depender solo de ese raw text y preserva señales útiles con `known_gaps` explícitos en vez de inventar datos.

## Outputs generated in `/outputs`

- `raw_extracted_text.txt`
- `extraction_quality.json`
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

- El parser documental en modo `good` sigue siendo V1 rule-based (keywords, regex y heurísticas simples).
- Si la calidad es baja, entra automáticamente el fallback híbrido.
- Si un campo no se detecta, se deja vacío y se registra en `known_gaps`.
- No se inventan valores faltantes.
