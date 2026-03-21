from __future__ import annotations

from typing import Any, Dict, List


def generate_qa_report(summary: Dict[str, Any], outline: List[Dict[str, Any]]) -> str:
    required_checks = {
        "max_8_slides": len(outline) <= 8,
        "includes_gameplay_or_video": any("video" in s["slide_title"].lower() or "video" in " ".join(s["content_blocks"]).lower() for s in outline),
        "includes_metrics_or_traction": any("traction" in s["slide_title"].lower() for s in outline),
        "includes_clear_ask": any("ask" in s["slide_title"].lower() for s in outline),
        "includes_team": any("team" in s["slide_title"].lower() for s in outline),
    }

    lines = ["# QA Report", "", "## Checklist de cumplimiento"]
    for check, status in required_checks.items():
        mark = "✅" if status else "❌"
        lines.append(f"- {mark} {check}")

    lines.extend(["", "## Huecos de información crítica"])
    for gap in summary["missing_critical_info"]:
        lines.append(f"- ⚠️ {gap}")

    lines.extend(
        [
            "",
            "## Claims dudosos o a validar",
            "- ⚠️ El nivel de interés relativo vs mercado se basa en inferencia, no benchmark externo verificable.",
            "",
            "## Recomendaciones finales",
            "- Solicitar métricas de retención (D1/D7) de la demo.",
            "- Añadir detalle de presupuesto de lanzamiento y uso de fondos.",
            "- Confirmar KPIs comerciales de Steam en ventana temporal consistente.",
        ]
    )

    return "\n".join(lines)
