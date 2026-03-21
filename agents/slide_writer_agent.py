from __future__ import annotations

from typing import Any, Dict, List


def _safe_list(value: Any) -> List[Any]:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


def _get_priority_message(strategy: Dict[str, Any], index: int, fallback: str) -> str:
    messages = strategy.get("priority_messages", [])
    if index < len(messages):
        return messages[index]
    return fallback


def _build_hook_slide(
    slide_number: int,
    summary: Dict[str, Any],
    strategy: Dict[str, Any],
) -> Dict[str, Any]:
    facts = summary["facts"]
    return {
        "slide_number": slide_number,
        "slide_title": f"{facts['game_name']} — Hook del juego",
        "slide_objective": "Captar interés inmediato con una propuesta de valor clara.",
        "key_message": _get_priority_message(strategy, 0, facts["USP"]),
        "content_blocks": [
            f"Fantasy principal: {facts['USP']}",
            f"Género: {facts['genre']}",
            f"Plataformas: {', '.join(_safe_list(facts['platform']))}",
            f"Estudio: {facts['studio_name']}",
        ],
        "suggested_visuals": ["Key art", "Logo", "Screenshot principal"],
        "source_reference": ["game_profile", "studio_profile", "assets"],
        "confidence_level": "high",
    }


def _build_gameplay_slide(
    slide_number: int,
    summary: Dict[str, Any],
    strategy: Dict[str, Any],
) -> Dict[str, Any]:
    facts = summary["facts"]
    return {
        "slide_number": slide_number,
        "slide_title": "Gameplay + prueba visual",
        "slide_objective": "Demostrar calidad de producto y claridad de gameplay.",
        "key_message": _get_priority_message(
            strategy,
            1,
            "El juego debe entenderse visualmente en pocos segundos.",
        ),
        "content_blocks": [
            "Vídeo o trailer de gameplay",
            "3 bullets del core loop",
            f"Estado de desarrollo: {facts['development_stage']}",
        ],
        "suggested_visuals": ["Gameplay video", "Capturas in-game", "GIF de loop principal"],
        "source_reference": ["assets", "game_profile"],
        "confidence_level": "high",
    }


def _build_traction_slide(
    slide_number: int,
    summary: Dict[str, Any],
    strategy: Dict[str, Any],
) -> Dict[str, Any]:
    facts = summary["facts"]
    traction = facts.get("traction_signals", {})

    wishlists = traction.get("steam_wishlists", "N/A")
    demo_downloads = traction.get("demo_downloads", "N/A")
    community_size = traction.get("community_size", "N/A")
    trailer_views = traction.get("trailer_views", "N/A")

    return {
        "slide_number": slide_number,
        "slide_title": "Tracción y validación",
        "slide_objective": "Mostrar señales reales de interés temprano.",
        "key_message": _get_priority_message(
            strategy,
            2,
            "Las señales iniciales apuntan a interés real antes del lanzamiento.",
        ),
        "content_blocks": [
            f"Steam wishlists: {wishlists}",
            f"Demo downloads: {demo_downloads}",
            f"Comunidad / followers: {community_size}",
            f"Trailer views / social proof: {trailer_views}",
        ],
        "suggested_visuals": ["Tarjetas KPI", "Mini gráfico", "Logos de festivales o validaciones"],
        "source_reference": ["traction"],
        "confidence_level": "high",
    }


def _build_market_slide(
    slide_number: int,
    summary: Dict[str, Any],
    strategy: Dict[str, Any],
) -> Dict[str, Any]:
    facts = summary["facts"]
    audience_type = strategy.get("audience_type", "mixed")

    market_angle = "Oportunidad de mercado y posicionamiento"
    if "publisher" in audience_type:
        market_angle = "Encaje editorial y marketability"
    elif "investor" in audience_type:
        market_angle = "Oportunidad de mercado y upside"

    return {
        "slide_number": slide_number,
        "slide_title": "Why now / oportunidad",
        "slide_objective": "Explicar por qué este juego merece atención ahora.",
        "key_message": _get_priority_message(
            strategy,
            3,
            market_angle,
        ),
        "content_blocks": [
            f"Audiencia objetivo: {facts['audience']}",
            "Posicionamiento frente a comparables",
            "Ventana de oportunidad / momentum",
        ],
        "suggested_visuals": ["Mapa de posicionamiento", "Comparables", "Trend snapshot"],
        "source_reference": ["business", "game_profile", "traction"],
        "confidence_level": "medium",
    }


def _build_business_slide(
    slide_number: int,
    summary: Dict[str, Any],
    strategy: Dict[str, Any],
) -> Dict[str, Any]:
    facts = summary["facts"]
    audience_type = strategy.get("audience_type", "mixed")

    content_blocks = [f"Modelo de negocio: {facts['business_model']}"]

    if "publisher" in audience_type:
        content_blocks.extend(
            [
                "Canales de lanzamiento previstos",
                "Racional de publishing / co-marketing",
                "Cómo un publisher acelera el go-to-market",
            ]
        )
    elif "investor" in audience_type:
        content_blocks.extend(
            [
                "Hipótesis de monetización",
                "Roadmap de crecimiento",
                "Uso potencial de capital / escalabilidad",
            ]
        )
    else:
        content_blocks.extend(
            [
                "Canales de lanzamiento previstos",
                "Plan de lanzamiento y distribución",
                "Lógica de monetización y partnership",
            ]
        )

    return {
        "slide_number": slide_number,
        "slide_title": "Modelo de negocio y plan de lanzamiento",
        "slide_objective": "Explicar cómo se convierte el interés en negocio.",
        "key_message": facts["business_model"],
        "content_blocks": content_blocks,
        "suggested_visuals": ["Timeline de lanzamiento", "Diagrama GTM", "Modelo simplificado"],
        "source_reference": ["business"],
        "confidence_level": "medium",
    }


def _build_team_slide(
    slide_number: int,
    summary: Dict[str, Any],
    strategy: Dict[str, Any],
) -> Dict[str, Any]:
    facts = summary["facts"]
    team = _safe_list(facts.get("team", []))
    team_size = len(team)

    return {
        "slide_number": slide_number,
        "slide_title": "Equipo",
        "slide_objective": "Reducir riesgo de ejecución mostrando credenciales del equipo.",
        "key_message": _get_priority_message(
            strategy,
            4,
            "El equipo presenta credenciales relevantes para ejecutar producto y lanzamiento.",
        ),
        "content_blocks": [
            f"Tamaño del equipo: {team_size}",
            "Roles clave y complementariedad",
            "Experiencia relevante / shipped titles / background",
        ],
        "suggested_visuals": ["Headshots", "Role cards", "Organigrama simple"],
        "source_reference": ["team", "studio_profile"],
        "confidence_level": "high",
    }


def _build_ask_slide(
    slide_number: int,
    summary: Dict[str, Any],
    strategy: Dict[str, Any],
) -> Dict[str, Any]:
    facts = summary["facts"]
    audience_type = strategy.get("audience_type", "mixed")

    ask_blocks = [f"Ask principal: {facts['current_ask']}"]

    if "publisher" in audience_type:
        ask_blocks.extend(
            [
                "Soporte editorial / publishing esperado",
                "Contribución en marketing, distribución o UA",
                "Siguiente paso propuesto: meeting / materials / build review",
            ]
        )
    elif "investor" in audience_type:
        ask_blocks.extend(
            [
                "Necesidad de financiación o partnership estratégico",
                "Uso esperado de fondos",
                "Siguiente paso propuesto: data room / follow-up / financial review",
            ]
        )
    else:
        ask_blocks.extend(
            [
                "Qué buscamos exactamente",
                "Qué tipo de partner encaja",
                "Siguiente paso propuesto",
            ]
        )

    return {
        "slide_number": slide_number,
        "slide_title": "El ask",
        "slide_objective": "Cerrar con una petición clara, concreta y accionable.",
        "key_message": facts["current_ask"],
        "content_blocks": ask_blocks,
        "suggested_visuals": ["Diagrama de partnership", "CTA final", "Timeline de next steps"],
        "source_reference": ["business"],
        "confidence_level": "high",
    }


def _build_risk_slide(
    slide_number: int,
    summary: Dict[str, Any],
    strategy: Dict[str, Any],
) -> Dict[str, Any]:
    risks = strategy.get("risks_to_compensate", [])
    if not risks:
        risks = ["No se han identificado riesgos relevantes en la estrategia actual."]

    return {
        "slide_number": slide_number,
        "slide_title": "Riesgos y mitigación",
        "slide_objective": "Abordar debilidades clave de forma honesta y estratégica.",
        "key_message": "El pitch reconoce riesgos y los enmarca con lógica de mitigación.",
        "content_blocks": risks[:3],
        "suggested_visuals": ["Tabla riesgo-mitigación"],
        "source_reference": ["strategy", "summary"],
        "confidence_level": "medium",
    }


def _build_slide(
    slide_type: str,
    slide_number: int,
    summary: Dict[str, Any],
    strategy: Dict[str, Any],
) -> Dict[str, Any]:
    normalized = slide_type.lower()

    if "hook" in normalized or "fantasy" in normalized:
        return _build_hook_slide(slide_number, summary, strategy)
    if "gameplay" in normalized or "video" in normalized:
        return _build_gameplay_slide(slide_number, summary, strategy)
    if "traction" in normalized or "validation" in normalized:
        return _build_traction_slide(slide_number, summary, strategy)
    if "why now" in normalized or "market" in normalized or "opportunity" in normalized:
        return _build_market_slide(slide_number, summary, strategy)
    if "business" in normalized or "launch" in normalized:
        return _build_business_slide(slide_number, summary, strategy)
    if "team" in normalized:
        return _build_team_slide(slide_number, summary, strategy)
    if "ask" in normalized or "next step" in normalized:
        return _build_ask_slide(slide_number, summary, strategy)
    if "risk" in normalized:
        return _build_risk_slide(slide_number, summary, strategy)

    return {
        "slide_number": slide_number,
        "slide_title": slide_type,
        "slide_objective": "Slide genérica derivada de la estrategia.",
        "key_message": "Pendiente de mayor especificación.",
        "content_blocks": [slide_type],
        "suggested_visuals": ["Por definir"],
        "source_reference": ["strategy"],
        "confidence_level": "low",
    }


def build_slides_outline(summary: Dict[str, Any], strategy: Dict[str, Any]) -> List[Dict[str, Any]]:
    recommended_order = strategy.get("recommended_slide_order", [])
    if not recommended_order:
        recommended_order = [
            "Hook + game fantasy",
            "Gameplay + video proof",
            "Traction and validation",
            "Why now / market opportunity",
            "Business model + launch plan",
            "Team credibility",
            "Clear ask + next step",
        ]

    slides = [
        _build_slide(slide_type, idx, summary, strategy)
        for idx, slide_type in enumerate(recommended_order[:8], start=1)
    ]

    return slides


def build_draft_deck(summary: Dict[str, Any], strategy: Dict[str, Any], outline: List[Dict[str, Any]]) -> str:
    """Renderiza el contenido del deck en Markdown para revisión rápida."""
    lines = [
        f"# Draft Deck — {summary['facts']['studio_name']}",
        "",
        f"Audience focus: **{strategy['audience_type']}**",
        "",
    ]

    for slide in outline:
        lines.append(f"## Slide {slide['slide_number']}: {slide['slide_title']}")
        lines.append(f"**Objective:** {slide['slide_objective']}")
        lines.append(f"**Key message:** {slide['key_message']}")
        lines.append("**Content blocks:**")
        for block in slide["content_blocks"]:
            lines.append(f"- {block}")
        lines.append(f"**Suggested visuals:** {', '.join(slide['suggested_visuals'])}")
        lines.append(f"**Confidence level:** {slide['confidence_level']}")
        lines.append(f"**Source reference:** {', '.join(slide['source_reference'])}")
        lines.append("")

    lines.extend(
        [
            "---",
            "### Data integrity notes",
            "- Facts are sourced from the ingestion payload.",
            "- Inferences should be validated before external use.",
            "- Missing critical data must be requested before final publisher/investor-facing delivery.",
        ]
    )

    return "\n".join(lines)
