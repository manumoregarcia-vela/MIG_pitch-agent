from __future__ import annotations

from typing import Any, Dict


def load_mock_studio_input() -> Dict[str, Any]:
    """Return a hardcoded mock input dataset for V1.

    The data is intentionally compact and includes explicit missing fields.
    """
    return {
        "studio_profile": {
            "studio_name": "Neon Lynx Studio",
            "location": "Madrid, Spain",
            "team_size": 12,
            "founded_year": 2021,
        },
        "game_profile": {
            "game_name": "Echoes of Titanium",
            "genre": "Action Roguelite",
            "platforms": ["PC (Steam)", "PlayStation 5"],
            "development_stage": "Public demo available; vertical slice complete",
            "core_fantasy": "High-speed mech combat in procedural arenas",
        },
        "traction": {
            "steam_wishlists": 38200,
            "demo_downloads": 9100,
            "discord_members": 6400,
            "youtube_trailer_views": 125000,
            "festival_selection": "Indie Arena Booth 2025 selection",
        },
        "business": {
            "business_model": "Premium game + cosmetic DLC",
            "target_audience": "Core PC/console players aged 18-34",
            "current_ask": "Publishing partner for global launch + co-marketing",
            "funding_status": "Pre-seed raised in 2023 (amount undisclosed)",
        },
        "team": [
            {
                "name": "Irene Soler",
                "role": "CEO / Game Director",
                "credential": "Former combat designer at MercurySteam",
            },
            {
                "name": "Dario Vega",
                "role": "CTO",
                "credential": "8 years in Unreal Engine multiplayer systems",
            },
            {
                "name": "Lucia Bernal",
                "role": "Art Director",
                "credential": "Ex-Platige Image, specialized in sci-fi pipelines",
            },
        ],
        "assets": {
            "gameplay_video": "https://example.com/echoes-gameplay-trailer",
            "press_kit": "https://example.com/neon-lynx-press-kit",
            "key_art": True,
            "logo_pack": True,
            "steam_page": "https://store.steampowered.com/app/1234567",
        },
        "source_map": {
            "studio_profile": "Founders questionnaire (2026-03-20)",
            "game_profile": "Internal one-pager v2",
            "traction": "Steam dashboard export (2026-03-18)",
            "business": "Founder interview notes",
            "team": "Team bio sheet",
            "assets": "Press kit index",
        },
        "known_gaps": [
            "No retention metrics from demo sessions",
            "No CPI/UA efficiency benchmarks",
            "No explicit launch budget split",
        ],
    }
