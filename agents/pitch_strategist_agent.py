from __future__ import annotations

from typing import Any, Dict, List


def build_structured_summary(mock_input: Dict[str, Any]) -> Dict[str, Any]:
    """Build structured summary while separating facts, inferences, and missing data."""
    traction = mock_input["traction"]

    facts = {
        "studio_name": mock_input["studio_profile"]["studio_name"],
        "game_name": mock_input["game_profile"]["game_name"],
        "genre": mock_input["game_profile"]["genre"],
        "platform": mock_input["game_profile"]["platforms"],
        "development_stage": mock_input["game_profile"]["development_stage"],
        "traction_signals": traction,
        "business_model": mock_input["business"]["business_model"],
        "audience": mock_input["business"]["target_audience"],
        "USP": mock_input["game_profile"]["core_fantasy"],
        "team": mock_input["team"],
        "current_ask": mock_input["business"]["current_ask"],
        "funding_status": mock_input["business"]["funding_status"],
        "proof_points": [
            "38.2k Steam wishlists",
            "9.1k demo downloads",
            "Selected for Indie Arena Booth 2025",
        ],
        "available_assets": mock_input["assets"],
    }

    inferences = [
        {
            "statement": "Current traction suggests above-average early market interest for an indie action roguelite.",
            "reasoning": "Wishlists + trailer views are strong relative to team size.",
            "confidence": "medium",
        },
        {
            "statement": "Publisher-first narrative should prioritize marketability and launch execution support.",
            "reasoning": "The ask is explicitly a publishing + co-marketing partnership.",
            "confidence": "high",
        },
    ]

    return {
        "facts": facts,
        "inferences": inferences,
        "missing_critical_info": mock_input["known_gaps"],
        "source_map": mock_input["source_map"],
    }


def recommend_strategy(summary: Dict[str, Any]) -> Dict[str, Any]:
    """Create a compact strategy recommendation from structured data."""
    missing: List[str] = summary["missing_critical_info"]

    return {
        "audience_type": "publisher-first (mixed-compatible)",
        "narrative_recommendation": (
            "Lead with product fantasy and proof of player pull, then de-risk execution "
            "with team credibility and clear publishing ask."
        ),
        "priority_messages": [
            "The game has a clear, marketable hook (high-speed mech roguelite fantasy).",
            "Early traction signals indicate meaningful player interest pre-launch.",
            "Team profile reduces execution risk for final production and launch.",
            "The studio needs a publisher for global distribution and co-marketing scale.",
        ],
        "risks_to_compensate": [
            "Missing retention metrics weakens long-term engagement argument.",
            "Unknown launch budget split reduces financial clarity.",
            "UA efficiency data is absent, limiting paid growth confidence.",
        ],
        "recommended_slide_order": [
            "Hook + game fantasy",
            "Gameplay + video proof",
            "Traction and validation",
            "Why now / market opportunity",
            "Business model + launch plan",
            "Team credibility",
            "Clear ask + next step",
        ],
        "open_questions": missing,
    }
