from __future__ import annotations

from typing import Any, Dict, List


def _safe_text(value: Any) -> str:
    return str(value or "").strip().lower()


def _infer_audience_type(current_ask: str) -> str:
    ask = _safe_text(current_ask)

    if any(token in ask for token in ["publish", "publisher", "co-marketing", "marketing"]):
        return "publisher"
    if any(token in ask for token in ["invest", "fund", "seed", "series", "equity"]):
        return "investor"
    if any(token in ask for token in ["platform", "distribution", "storefront"]):
        return "platform"
    if any(token in ask for token in ["grant", "public funding", "subsidy"]):
        return "grant"
    return "general-partner"


def _score_dimension(summary: Dict[str, Any], audience_type: str) -> Dict[str, int]:
    facts = summary["facts"]
    missing = summary["missing_critical_info"]

    traction = facts.get("traction_signals", {})
    team = facts.get("team", [])

    product_score = 2
    if facts.get("USP"):
        product_score += 1
    if facts.get("development_stage"):
        product_score += 1
    if facts.get("available_assets", {}).get("gameplay_video"):
        product_score += 1

    traction_score = 2
    numeric_signals = [
        traction.get("steam_wishlists", 0),
        traction.get("demo_downloads", 0),
        traction.get("youtube_trailer_views", 0),
        traction.get("discord_members", 0),
    ]
    if any(v and v > 0 for v in numeric_signals):
        traction_score += 1
    if any(v and v >= 10000 for v in numeric_signals):
        traction_score += 1
    if traction.get("festival_selection"):
        traction_score += 1

    market_score = 2
    if facts.get("genre"):
        market_score += 1
    if facts.get("audience"):
        market_score += 1
    if "market" in _safe_text(facts.get("audience")):
        market_score += 1

    business_model_score = 2
    if facts.get("business_model"):
        business_model_score += 1
    if facts.get("funding_status"):
        business_model_score += 1
    if not any("budget" in _safe_text(gap) for gap in missing):
        business_model_score += 1

    team_score = 2
    if team:
        team_score += 1
    if len(team) >= 3:
        team_score += 1
    if any(_safe_text(member.get("credential")) for member in team if isinstance(member, dict)):
        team_score += 1

    ask_score = 2
    current_ask = facts.get("current_ask")
    if current_ask:
        ask_score += 1
    if audience_type != "general-partner":
        ask_score += 1
    if not any("ask" in _safe_text(gap) or "budget" in _safe_text(gap) for gap in missing):
        ask_score += 1

    return {
        "product": min(product_score, 5),
        "traction": min(traction_score, 5),
        "market": min(market_score, 5),
        "business_model": min(business_model_score, 5),
        "team": min(team_score, 5),
        "ask": min(ask_score, 5),
    }


def build_structured_summary(mock_input: Dict[str, Any]) -> Dict[str, Any]:
    """Build structured summary while separating facts, inferences, and missing data."""

    facts = {
        "studio_name": mock_input["studio_profile"]["studio_name"],
        "game_name": mock_input["game_profile"]["game_name"],
        "genre": mock_input["game_profile"]["genre"],
        "platform": mock_input["game_profile"]["platforms"],
        "development_stage": mock_input["game_profile"]["development_stage"],
        "traction_signals": mock_input["traction"],
        "business_model": mock_input["business"]["business_model"],
        "audience": mock_input["business"]["target_audience"],
        "USP": mock_input["game_profile"]["core_fantasy"],
        "team": mock_input["team"],
        "current_ask": mock_input["business"]["current_ask"],
        "funding_status": mock_input["business"]["funding_status"],
        "available_assets": mock_input["assets"],
    }

    inferences: List[Dict[str, str]] = []
    if facts["current_ask"]:
        inferences.append(
            {
                "statement": "Primary pitch audience can be inferred from the current ask.",
                "reasoning": "Ask wording indicates target partner type.",
                "confidence": "medium",
            }
        )

    return {
        "facts": facts,
        "inferences": inferences,
        "missing_critical_info": mock_input["known_gaps"],
        "source_map": mock_input["source_map"],
    }


def recommend_strategy(summary: Dict[str, Any]) -> Dict[str, Any]:
    """Create a compact strategy recommendation from structured data."""
    facts = summary["facts"]
    missing: List[str] = summary["missing_critical_info"]

    audience_type = _infer_audience_type(facts.get("current_ask", ""))
    scores = _score_dimension(summary, audience_type)

    weak_dimensions = [k for k, v in scores.items() if v <= 3]

    priority_messages: List[str] = []
    if scores["product"] >= 4:
        priority_messages.append("Lead with product hook plus gameplay proof in the first minute.")
    if scores["traction"] >= 4:
        priority_messages.append("Use strongest traction signals as external validation before roadmap slides.")
    if scores["team"] >= 4:
        priority_messages.append("Frame team credentials as execution de-risking for launch readiness.")
    if scores["ask"] >= 4:
        priority_messages.append(f"State a crisp {audience_type}-oriented ask with expected partner contribution.")
    if not priority_messages:
        priority_messages.append("Open with the most concrete validated fact, then move quickly to the specific ask.")

    risks_to_compensate: List[str] = []
    for gap in missing:
        risks_to_compensate.append(f"Address missing data: {gap}.")
    for dimension in weak_dimensions:
        risks_to_compensate.append(f"Strengthen {dimension} evidence to reduce diligence friction.")

    return {
        "audience_type": audience_type,
        "scores": scores,
        "narrative_recommendation": (
            "Use a fact-first sequence: product clarity -> traction proof -> market/business viability -> "
            "team credibility -> specific ask. Keep each section tied to available evidence only."
        ),
        "priority_messages": priority_messages[:4],
        "risks_to_compensate": risks_to_compensate[:5],
        "recommended_slide_order": [
            "Hook + product clarity",
            "Gameplay proof",
            "Traction validation",
            "Market + business model",
            "Team credibility",
            "Specific ask + partner fit",
        ],
        "open_questions": missing,
    }
