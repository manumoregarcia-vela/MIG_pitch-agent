from __future__ import annotations

from typing import Any, Dict, List


def _contains_any(text: str, keywords: List[str]) -> bool:
    text = text.lower()
    return any(keyword in text for keyword in keywords)


def _score_label(score: int) -> str:
    if score >= 5:
        return "Excelente"
    if score == 4:
        return "Sólido"
    if score == 3:
        return "Aceptable"
    if score == 2:
        return "Débil"
    return "Muy débil"


def generate_qa_report(
    summary: Dict[str, Any],
    strategy: Dict[str, Any],
    outline: List[Dict[str, Any]],
) -> str:
    slide_texts = [
        (
            slide.get("slide_title", "") + " " + " ".join(slide.get("content_blocks", []))
        ).lower()
        for slide in outline
    ]

    required_checks = {
        "max_8_slides": len(outline) <= 8,
        "includes_gameplay_or_video": any(
            _contains_any(text, ["video", "gameplay", "trailer", "footage"])
            for text in slide_texts
        ),
        "includes_metrics_or_traction": any(
            _contains_any(
                text,
                [
                    "traction",
                    "tracción",
                    "kpi",
                    "metric",
                    "metrics",
                    "wishlist",
                    "wishlists",
                    "retention",
                    "validación",
                    "validation",
                    "downloads",
                ],
            )
            for text in slide_texts
        ),
        "includes_clear_ask": any(
            _contains_any(
                text,
                ["ask", "buscamos", "publisher", "publishing", "investment", "funding", "raise"]
            )
            for text in slide_texts
        ),
        "includes_team": any(
            _contains_any(text, ["team", "equipo", "founders", "leadership"])
            for text in slide_texts
        ),
    }

    missing_info = summary.get("missing_critical_info", [])
    audience_type = strategy.get("audience_type", "mixed")
    priority_messages = strategy.get("priority_messages", [])
    risks_to_compensate = strategy.get("risks_to_compensate", [])

    clarity = 5 if required_checks["includes_gameplay_or_video"] and len(outline) <= 8 else 3

    credibility = 4
    if len(missing_info) > 2:
        credibility = 2
    elif len(missing_info) > 0:
        credibility = 3

    traction_strength = 4 if required_checks["includes_metrics_or_traction"] else 2
    differentiation = 4 if priority_messages else 2
    appeal = 4 if required_checks["includes_clear_ask"] and required_checks["includes_team"] else 2

    demo_day_readiness = round(
        (clarity + credibility + traction_strength + differentiation + appeal) / 5,
        1,
    )

    recommendations: List[str] = []

    if not required_checks["includes_gameplay_or_video"]:
        recommendations.append(
            "Añadir un bloque o slide con gameplay/video claro en la primera mitad del deck."
        )

    if not required_checks["includes_metrics_or_traction"]:
        recommendations.append(
            "Reforzar la validación con métricas, wishlists, playtest feedback o señales concretas de tracción."
        )

    if not required_checks["includes_clear_ask"]:
        recommendations.append(
            "Definir con más precisión qué busca el estudio: publisher, inversión, partnership o financiación concreta."
        )

    if not required_checks["includes_team"]:
        recommendations.append(
            "Reforzar la credibilidad del equipo con experiencia relevante, roles clave o títulos enviados al mercado."
        )

    if len(missing_info) > 2:
        recommendations.append(
            "Reducir incertidumbre completando los datos críticos faltantes antes de usar este pitch en un entorno real."
        )

    if audience_type == "mixed":
        recommendations.append(
            "Equilibrar mejor marketability del juego con credibilidad de negocio para una audiencia mixta publisher + investor."
        )
    elif "publisher" in audience_type:
        recommendations.append(
            "Asegurar que el pitch enfatiza marketability, encaje editorial y capacidad de ejecución de lanzamiento."
        )
    elif "investor" in audience_type:
        recommendations.append(
            "Asegurar que el pitch enfatiza escalabilidad, uso de fondos y potencial de retorno."
        )

    if risks_to_compensate:
        recommendations.append(
            "Alinear la narrativa del deck con los riesgos detectados para compensar debilidades de forma explícita."
        )

    if not recommendations:
        recommendations.append(
            "El pitch está razonablemente bien planteado para una V1; el siguiente paso es refinar narrativa y diseño visual."
        )

    lines = [
        "# QA Report",
        "",
        "## Evaluación general",
        f"- Audiencia objetivo evaluada: **{audience_type}**",
        f"- Demo Day readiness score: **{demo_day_readiness}/5**",
        "",
        "## Scoring de calidad",
        f"- Claridad: **{clarity}/5** ({_score_label(clarity)})",
        f"- Credibilidad: **{credibility}/5** ({_score_label(credibility)})",
        f"- Fuerza de tracción: **{traction_strength}/5** ({_score_label(traction_strength)})",
        f"- Diferenciación: **{differentiation}/5** ({_score_label(differentiation)})",
        f"- Atractivo para publisher/inversor: **{appeal}/5** ({_score_label(appeal)})",
        "",
        "## Checklist de cumplimiento",
    ]

    for check, status in required_checks.items():
        mark = "✅" if status else "❌"
        lines.append(f"- {mark} {check}")

    lines.extend(["", "## Mensajes prioritarios detectados en estrategia"])
    if priority_messages:
        for message in priority_messages:
            lines.append(f"- {message}")
    else:
        lines.append("- ⚠️ La estrategia no define mensajes prioritarios claros.")

    lines.extend(["", "## Riesgos o debilidades a compensar"])
    if risks_to_compensate:
        for risk in risks_to_compensate:
            lines.append(f"- ⚠️ {risk}")
    else:
        lines.append("- ✅ No se han identificado riesgos relevantes en la estrategia actual.")

    lines.extend(["", "## Huecos de información crítica"])
    if missing_info:
        for gap in missing_info:
            lines.append(f"- ⚠️ {gap}")
    else:
        lines.append("- ✅ No se detectan huecos críticos en el input actual.")

    lines.extend(["", "## Claims dudosos o a validar"])
    lines.append("- ⚠️ Validar benchmarks externos y comparables de mercado antes del Demo Day.")
    if not required_checks["includes_metrics_or_traction"]:
        lines.append("- ⚠️ La narrativa de validación parece insuficiente o demasiado genérica.")

    lines.extend(["", "## Recomendaciones finales"])
    for recommendation in recommendations:
        lines.append(f"- {recommendation}")

    return "\n".join(lines)
