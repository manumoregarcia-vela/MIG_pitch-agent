from __future__ import annotations

from typing import Any, Dict, List


def _safe_list(value: Any) -> List[Any]:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


def _infer_audience_type(current_ask: str) -> str:
    ask = current_ask.lower()

    has_publisher = any(term in ask for term in ["publisher", "publishing", "co-marketing", "distribution"])
    has_investor = any(term in ask for term in ["investment", "funding", "raise", "capital", "financing"])

    if has_publisher and has_investor:
        return "mixed"
    if has_publisher:
        return "publisher-first"
    if has_investor:
        return "investor-first"
    return "mixed"


def _build_proof_points(traction: Dict[str, Any], source_map: Dict[str, Any]) -> List[str]:
    proof_points: List[str] = []

    if traction.get("steam_wishlists"):
        proof_points.append(f"{traction['steam_wishlists']:,} Steam wishlists")

    if traction.get("demo_downloads"):
        proof_points.append(f"{traction['demo_downloads']:,} demo downloads")

    if traction.get("trailer_views"):
        proof_points.append(f"{traction['trailer_views']:,} trailer views")

    if traction.get("community_size"):
        proof_points.append(f"{traction['community_size']:,} community members/followers")

    if source_map.get("festival_validation"):
        proof_points.append(str(source_map["festival_validation"]))

    return proof_points


def build_structured_summary(mock_input: Dict[str, Any]) -> Dict[str, Any]:
    """Build structured summary while separating facts, inferences, and missing data."""
    traction = mock_input.get("traction", {})
    studio_profile = mock_input.get("studio_profile", {})
    game_profile = mock_input.get("game_profile", {})
    business = mock_input.get("business", {})
    team = mock_input.get("team", [])
    assets = mock_input.get("assets", {})
    source_map = mock_input.get("source_map", {})
    known_gaps = mock_input.get("known_gaps", [])

    facts = {
        "studio_name": studio_profile.get("studio_name", "Unknown Studio"),
        "game_name": game_profile.get("game_name", "Unknown Game"),
        "genre": game_profile.get("genre", "Unknown Genre"),
        "platform": _safe_list(game_profile.get("platforms", [])),
        "development_stage": game_profile.get("development_stage", "Unknown Stage"),
        "traction_signals": traction,
        "business_model": business.get("business_model", "Unknown business model"),
        "audience": business.get("target_audience", "Unknown audience"),
        "USP": game_profile.get("core_fantasy", "No core fantasy provided"),
        "team": team,
        "current_ask": business.get("current_ask", "No ask defined"),
        "funding_status": business.get("funding_status", "Unknown funding status"),
        "proof_points": _build_proof_points(traction, source_map),
        "available_assets": assets,
    }

    inferences: List[Dict[str, str]] = []

    if traction.get("steam_wishlists", 0) >= 10000:
        inferences.append(
            {
                "statement": "Las señales iniciales sugieren interés real del mercado antes del lanzamiento.",
                "reasoning": "El volumen de wishlists es relevante para una fase pre-launch.",
                "confidence": "medium",
            }
        )

    if "publisher" in facts["current_ask"].lower():
        inferences.append(
            {
                "statement": "La narrativa debería enfatizar marketability, lanzamiento y encaje editorial.",
                "reasoning": "El ask se orienta a publishing y distribución.",
                "confidence": "high",
            }
        )

    if len(known_gaps) > 2:
        inferences.append(
            {
                "statement": "La credibilidad del pitch depende de compensar bien los gaps de información.",
                "reasoning": "Faltan varios datos críticos para una conversación avanzada con inversores o publishers.",
                "confidence": "high",
            }
        )

    return {
        "facts": facts,
        "inferences": inferences,
        "missing_critical_info": known_gaps,
        "source_map": source_map,
    }


def _score_product(facts: Dict[str, Any]) -> Dict[str, Any]:
    usp = facts.get("USP", "")
    assets = facts.get("available_assets", {})

    score = 3
    reason = "La propuesta de producto es comprensible pero todavía genérica."

    if usp and len(str(usp)) > 20:
        score = 4
        reason = "La fantasy central del juego está relativamente clara."

    if assets.get("gameplay_video") or assets.get("trailer"):
        score = min(score + 1, 5)
        reason += " Además, existen assets visuales para demostrar el producto."

    return {"score": score, "reason": reason}


def _score_traction(facts: Dict[str, Any], missing: List[str]) -> Dict[str, Any]:
    traction = facts.get("traction_signals", {})
    wishlists = traction.get("steam_wishlists", 0)
    downloads = traction.get("demo_downloads", 0)

    if wishlists >= 30000 or downloads >= 10000:
        score = 5
        reason = "Las señales tempranas de demanda son fuertes."
    elif wishlists >= 10000 or downloads >= 3000:
        score = 4
        reason = "La tracción inicial es prometedora."
    elif wishlists >= 3000 or downloads >= 1000:
        score = 3
        reason = "Hay validación inicial, aunque aún limitada."
    else:
        score = 2
        reason = "La validación cuantitativa todavía es débil o insuficiente."

    if any("retention" in gap.lower() for gap in missing):
        reason += " La ausencia de métricas de retención reduce confianza."

    return {"score": score, "reason": reason}


def _score_market(facts: Dict[str, Any]) -> Dict[str, Any]:
    genre = str(facts.get("genre", "")).lower()
    audience = str(facts.get("audience", "")).lower()

    score = 3
    reason = "El posicionamiento de mercado es aceptable pero aún poco específico."

    if genre and audience:
        score = 4
        reason = "Existe una definición razonable de género y audiencia objetivo."

    return {"score": score, "reason": reason}


def _score_business_model(facts: Dict[str, Any], missing: List[str]) -> Dict[str, Any]:
    business_model = str(facts.get("business_model", "")).lower()
    score = 2
    reason = "El modelo de negocio todavía es poco claro."

    if business_model and business_model != "unknown business model":
        score = 3
        reason = "Existe una base de modelo de negocio definida."

    if not any("budget" in gap.lower() or "fund" in gap.lower() for gap in missing):
        score += 1
        reason += " Además, no aparecen grandes lagunas financieras en el input."

    return {"score": min(score, 5), "reason": reason}


def _score_team(facts: Dict[str, Any]) -> Dict[str, Any]:
    team = _safe_list(facts.get("team", []))
    size = len(team)

    if size >= 6:
        return {
            "score": 4,
            "reason": "El equipo parece suficientemente dimensionado para ejecutar el proyecto.",
        }
    if size >= 3:
        return {
            "score": 3,
            "reason": "El equipo tiene una base operativa razonable, aunque aún puede requerir refuerzos.",
        }
    return {
        "score": 2,
        "reason": "El equipo parece reducido para el alcance potencial del proyecto.",
    }


def _score_ask(facts: Dict[str, Any]) -> Dict[str, Any]:
    ask = str(facts.get("current_ask", "")).strip()

    if not ask or ask.lower() == "no ask defined":
        return {
            "score": 1,
            "reason": "No hay un ask claro definido.",
        }

    if len(ask) > 20:
        return {
            "score": 4,
            "reason": "El ask existe y parece lo bastante específico para una conversación inicial.",
        }

    return {
        "score": 3,
        "reason": "El ask está presente, pero puede ser más concreto.",
    }


def score_pitch(summary: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    facts = summary["facts"]
    missing = summary["missing_critical_info"]

    return {
        "product": _score_product(facts),
        "traction": _score_traction(facts, missing),
        "market": _score_market(facts),
        "business_model": _score_business_model(facts, missing),
        "team": _score_team(facts),
        "ask": _score_ask(facts),
    }


def _build_priority_messages(
    facts: Dict[str, Any],
    scores: Dict[str, Dict[str, Any]],
    audience_type: str,
) -> List[str]:
    messages: List[str] = []

    messages.append(f"El juego ofrece una propuesta central clara: {facts['USP']}.")

    if scores["traction"]["score"] >= 4:
        messages.append("Las señales tempranas de tracción sugieren interés real antes del lanzamiento.")
    else:
        messages.append("La narrativa debe reforzar validación cualitativa mientras madura la tracción.")

    if scores["team"]["score"] >= 4:
        messages.append("El equipo ayuda a reducir el riesgo de ejecución en producción y go-to-market.")
    else:
        messages.append("La credibilidad del equipo debe explicarse mejor para compensar riesgo de ejecución.")

    if audience_type == "publisher-first":
        messages.append("El caso debe enfatizar marketability, encaje editorial y soporte de lanzamiento.")
    elif audience_type == "investor-first":
        messages.append("El caso debe enfatizar escalabilidad, uso de fondos y potencial de retorno.")
    else:
        messages.append("El pitch debe equilibrar atractivo editorial con credibilidad de negocio.")

    return messages[:4]


def _build_risks_to_compensate(
    missing: List[str],
    scores: Dict[str, Dict[str, Any]],
) -> List[str]:
    risks: List[str] = []

    if scores["traction"]["score"] <= 3:
        risks.append("La tracción todavía no demuestra de forma contundente el potencial comercial.")

    if scores["business_model"]["score"] <= 3:
        risks.append("La lógica de negocio y monetización necesita mayor claridad.")

    if scores["team"]["score"] <= 3:
        risks.append("La narrativa del equipo puede no ser suficiente para reducir el riesgo de ejecución.")

    for gap in missing[:3]:
        risks.append(gap)

    return risks[:4]


def _recommended_slide_order(audience_type: str, scores: Dict[str, Dict[str, Any]]) -> List[str]:
    base_order = [
        "Hook + game fantasy",
        "Gameplay + video proof",
        "Traction and validation",
        "Why now / market opportunity",
        "Business model + launch plan",
        "Team credibility",
        "Clear ask + next step",
    ]

    if audience_type == "publisher-first":
        return [
            "Hook + game fantasy",
            "Gameplay + video proof",
            "Traction and validation",
            "Why now / market opportunity",
            "Business model + launch plan",
            "Team credibility",
            "Clear ask + next step",
        ]

    if audience_type == "investor-first":
        return [
            "Hook + game fantasy",
            "Traction and validation",
            "Why now / market opportunity",
            "Business model + launch plan",
            "Team credibility",
            "Clear ask + next step",
            "Gameplay + video proof",
        ]

    if scores["traction"]["score"] <= 2:
        return [
            "Hook + game fantasy",
            "Gameplay + video proof",
            "Why now / market opportunity",
            "Team credibility",
            "Business model + launch plan",
            "Clear ask + next step",
        ]

    return base_order


def recommend_strategy(summary: Dict[str, Any]) -> Dict[str, Any]:
    facts = summary["facts"]
    missing = summary["missing_critical_info"]

    audience_type = _infer_audience_type(facts["current_ask"])
    scores = score_pitch(summary)
    priority_messages = _build_priority_messages(facts, scores, audience_type)
    risks_to_compensate = _build_risks_to_compensate(missing, scores)
    recommended_slide_order = _recommended_slide_order(audience_type, scores)

    if audience_type == "publisher-first":
        narrative_recommendation = (
            "Abrir con fantasy y calidad de producto, demostrar marketability con gameplay y tracción, "
            "y cerrar con un ask claro de publishing/co-marketing."
        )
    elif audience_type == "investor-first":
        narrative_recommendation = (
            "Abrir con una visión clara del producto, demostrar señales de validación, "
            "explicar oportunidad de negocio y cerrar con un ask de inversión bien definido."
        )
    else:
        narrative_recommendation = (
            "Equilibrar claridad de producto, señales de validación, credibilidad del equipo "
            "y una propuesta de partnership/inversión accionable."
        )

    key_selling_points = [
        facts["USP"],
        *facts.get("proof_points", [])[:2],
        facts["current_ask"],
    ]

    return {
        "audience_type": audience_type,
        "scores": scores,
        "narrative_recommendation": narrative_recommendation,
        "priority_messages": priority_messages,
        "risks_to_compensate": risks_to_compensate,
        "recommended_slide_order": recommended_slide_order,
        "key_selling_points": key_selling_points,
        "open_questions": missing,
    }
