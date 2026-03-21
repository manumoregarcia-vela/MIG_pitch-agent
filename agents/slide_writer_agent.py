from __future__ import annotations

from typing import Any, Dict, List


def build_slides_outline(summary: Dict[str, Any], strategy: Dict[str, Any]) -> List[Dict[str, Any]]:
    facts = summary["facts"]
    traction = facts["traction_signals"]

    return [
        {
            "slide_number": 1,
            "slide_title": f"{facts['game_name']} — Fast, Skillful Mech Combat",
            "slide_objective": "Capture immediate interest with a clear product hook.",
            "key_message": facts["USP"],
            "content_blocks": [
                "One-line fantasy statement",
                "Genre + platform badges",
                "Studio identity",
            ],
            "suggested_visuals": ["Key art", "Logo"],
            "source_reference": ["game_profile", "studio_profile", "assets"],
            "confidence_level": "high",
        },
        {
            "slide_number": 2,
            "slide_title": "Gameplay Proof",
            "slide_objective": "Demonstrate game quality and marketability through video.",
            "key_message": "Gameplay loop is visually strong and trailer-ready.",
            "content_blocks": ["Gameplay video link", "3 core loop bullets", "Screenshot strip"],
            "suggested_visuals": ["Gameplay trailer embed", "In-game screenshots"],
            "source_reference": ["assets", "game_profile"],
            "confidence_level": "high",
        },
        {
            "slide_number": 3,
            "slide_title": "Traction Signals",
            "slide_objective": "Show validated early interest from players.",
            "key_message": (
                f"{traction['steam_wishlists']:,} wishlists and {traction['demo_downloads']:,} "
                "demo downloads show demand before launch."
            ),
            "content_blocks": [
                "Wishlist KPI",
                "Demo downloads KPI",
                "Community + trailer social proof",
            ],
            "suggested_visuals": ["KPI cards", "Simple growth chart"],
            "source_reference": ["traction"],
            "confidence_level": "high",
        },
        {
            "slide_number": 4,
            "slide_title": "Why This Opportunity, Why Now",
            "slide_objective": "Frame timing and strategic relevance for publishers/investors.",
            "key_message": "A proven genre + polished demo creates a timely launch window.",
            "content_blocks": ["Genre momentum statement", "Festival validation", "Execution timing"],
            "suggested_visuals": ["Positioning matrix"],
            "source_reference": ["game_profile", "traction"],
            "confidence_level": "medium",
        },
        {
            "slide_number": 5,
            "slide_title": "Business Model & Launch Plan",
            "slide_objective": "Explain monetization logic and go-to-market intent.",
            "key_message": facts["business_model"],
            "content_blocks": ["Revenue model", "Launch channels", "Co-marketing rationale"],
            "suggested_visuals": ["Go-to-market timeline"],
            "source_reference": ["business"],
            "confidence_level": "medium",
        },
        {
            "slide_number": 6,
            "slide_title": "Team",
            "slide_objective": "Reduce execution risk with relevant team credentials.",
            "key_message": "The core team has direct experience shipping high-quality action titles.",
            "content_blocks": ["Founder bios", "Role-fit highlights", "Team size and setup"],
            "suggested_visuals": ["Headshots", "Role cards"],
            "source_reference": ["team", "studio_profile"],
            "confidence_level": "high",
        },
        {
            "slide_number": 7,
            "slide_title": "The Ask",
            "slide_objective": "End with a clear and actionable partnership request.",
            "key_message": facts["current_ask"],
            "content_blocks": ["Partnership ask", "Expected publisher contribution", "Next meeting CTA"],
            "suggested_visuals": ["Partnership model diagram"],
            "source_reference": ["business"],
            "confidence_level": "high",
        },
    ]


def build_draft_deck(summary: Dict[str, Any], strategy: Dict[str, Any], outline: List[Dict[str, Any]]) -> str:
    """Render slide content in Markdown for fast review."""
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
        lines.append("")

    lines.extend(
        [
            "---",
            "### Data integrity notes",
            "- Facts are sourced from the mock ingestion payload.",
            "- Inferences are marked in `structured_summary.json` and should be validated in V2.",
            "- Missing critical data must be requested before final investor-facing delivery.",
        ]
    )

    return "\n".join(lines)
