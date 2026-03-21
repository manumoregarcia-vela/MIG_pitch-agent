# MIG_pitch-agent

Demo Day-oriented pitch strategy generator for game studios.

## Overview

Sistema de agentes para generar y optimizar pitches de videojuegos (5-8 slides) orientados a Demo Day, maximizando interés de publishers e inversores.

---

## What this version implements

### Core capabilities

- Generación de estrategia de pitch basada en un framework de evaluación.
- Adaptación de narrativa según audiencia:
  - `mixed` (default)
  - `publisher-first`
  - `investor-first`
- Priorización de contenido para decks de 5-8 slides:
  - claridad de gameplay
  - tracción
  - diferenciación
  - credibilidad de ejecución
- Detección de debilidades y compensación narrativa.

---

## Evaluation framework

Scoring explícito (1–5) en:

- `product`
- `traction`
- `market`
- `business_model`
- `team`
- `ask`

Incluye:
- separación de `facts`, `inferences` y `missing_critical_info`
- narrativa optimizada para Demo Day
- posicionamiento, riesgos y key selling points

---

## Pipeline

Pipeline end-to-end que genera automáticamente:

- `outputs/structured_summary.json`
- `outputs/pitch_strategy.md`
- `outputs/slides_outline.json`
- `outputs/draft_deck.md`
- `outputs/qa_report.md`

---

## Architecture

- `ingestion` (mock input)
- `pitch_strategist` (evaluación + narrativa)
- `slide_writer`
- `qa_agent`

---

## Project structure

- `agents/`: lógica de agentes
- `pipeline/`: orquestación
- `outputs/`: artefactos generados
- `app.py`: entrypoint

---

## Usage

### Simple run (full pipeline)

```bash
python app.py
