from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple


SCORING_DIMENSIONS = [
    "product",
    "traction",
    "market",
    "business_model",
    "team",
    "ask",
]


@dataclass
class ScoreResult:
    score: int
    reasoning: str


class PitchStrategistAgent:
    """Demo Day-focused strategist for gaming publishers + investors."""

    def __init__(self, default_audience: str = "mixed") -> None:
        self.default_audience = default_audience

    def build_strategy(self, studio_data: Dict[str, Any], audience: str | None = None) -> Dict[str, Any]:
        selected_audience = audience or self.default_audience
        scores = self._score(studio_data)
        weak_areas = self._detect_weaknesses(scores)

        narrative_angle = self._narrative_angle(studio_data, scores, selected_audience)
        key_selling_points = self._key_selling_points(studio_data, scores)
        risks_and_positioning = self._risks_and_positioning(weak_areas)
        slide_plan = self._slide_priorities(studio_data, selected_audience, weak_areas)

        return {
            "audience": selected_audience,
            "narrative_angle": narrative_angle,
            "scoring_breakdown": {
                metric: {
                    "score": result.score,
                    "reasoning": result.reasoning,
                }
                for metric, result in scores.items()
            },
            "key_selling_points": key_selling_points,
            "weakness_detection": weak_areas,
            "risks": [item["risk"] for item in risks_and_positioning],
            "how_to_position_them": [item["positioning"] for item in risks_and_positioning],
            "recommended_slides": slide_plan,
        }

    def render_pitch_strategy_md(self, strategy: Dict[str, Any]) -> str:
        lines: List[str] = []
        lines.append("# pitch_strategy")
        lines.append("")
        lines.append("## Narrative angle")
        lines.append(strategy["narrative_angle"])
        lines.append("")

        lines.append("## Scoring breakdown (1-5)")
        for metric in SCORING_DIMENSIONS:
            metric_data = strategy["scoring_breakdown"][metric]
            lines.append(f"- **{metric}**: {metric_data['score']}/5 — {metric_data['reasoning']}")
        lines.append("")

        lines.append("## Key selling points")
        for point in strategy["key_selling_points"]:
            lines.append(f"- {point}")
        lines.append("")

        lines.append("## Risks")
        for risk in strategy["risks"]:
            lines.append(f"- {risk}")
        lines.append("")

        lines.append("## How to position them")
        for positioning in strategy["how_to_position_them"]:
            lines.append(f"- {positioning}")
        lines.append("")

        lines.append("## Weakness detection + compensation")
        if not strategy["weakness_detection"]:
            lines.append("- No critical weaknesses detected. Maintain momentum and keep proof density high.")
        else:
            for item in strategy["weakness_detection"]:
                lines.append(
                    f"- **{item['area']}** ({item['score']}/5): {item['why_weak']}. "
                    f"Compensate with: {item['compensation_narrative']}"
                )
        lines.append("")

        lines.append("## Recommended slide order (5-8 max)")
        for slide in strategy["recommended_slides"]:
            lines.append(f"{slide['slide_number']}. **{slide['title']}** — {slide['objective']}")

        return "\n".join(lines)

    def _score(self, studio_data: Dict[str, Any]) -> Dict[str, ScoreResult]:
        gameplay = bool(studio_data.get("gameplay_video") or studio_data.get("product_demo"))
        usp = bool(studio_data.get("USP"))
        traction_signals = studio_data.get("traction_signals", [])
        proof_points = studio_data.get("proof_points", [])
        market = studio_data.get("market", "")
        business_model = studio_data.get("business_model", "")
        team = studio_data.get("team", [])
        ask = studio_data.get("current_ask", "")

        scores: Dict[str, ScoreResult] = {}
        product_score = min(5, (2 if gameplay else 1) + (2 if usp else 1))
        scores["product"] = ScoreResult(
            score=product_score,
            reasoning="Gameplay clarity and unique hook are "
            + ("well evidenced." if gameplay and usp else "partially evidenced; strengthen visual proof."),
        )

        traction_score = 1
        if len(traction_signals) >= 3:
            traction_score = 5
        elif len(traction_signals) == 2:
            traction_score = 4
        elif len(traction_signals) == 1:
            traction_score = 3
        elif proof_points:
            traction_score = 2
        scores["traction"] = ScoreResult(
            score=traction_score,
            reasoning="Based on quantity and concreteness of KPIs / external validation signals.",
        )

        market_score = 4 if market else 2
        scores["market"] = ScoreResult(
            score=market_score,
            reasoning="Market opportunity framing is " + ("explicit." if market else "underdeveloped; needs category size + timing."),
        )

        model_score = 4 if business_model else 2
        scores["business_model"] = ScoreResult(
            score=model_score,
            reasoning="Monetization and go-to-market are " + ("clear enough for a first pass." if business_model else "not explicit yet."),
        )

        team_score = 5 if len(team) >= 4 else 4 if len(team) >= 2 else 2
        scores["team"] = ScoreResult(
            score=team_score,
            reasoning="Execution credibility inferred from team completeness and leadership coverage.",
        )

        ask_score = 5 if ask and any(t in ask.lower() for t in ["fund", "publish", "budget", "milestone", "€", "$", "runway"]) else 2
        scores["ask"] = ScoreResult(
            score=ask_score,
            reasoning="Ask is " + ("specific and decision-friendly." if ask_score >= 4 else "too vague; define amount, use of funds, and expected partner role."),
        )

        return scores

    def _detect_weaknesses(self, scores: Dict[str, ScoreResult]) -> List[Dict[str, Any]]:
        compensation_playbook = {
            "product": "Lead with 20-30 seconds of best gameplay loop and immediate player fantasy before any text.",
            "traction": "Swap vanity claims for directional proof: playtests, retention proxy, wishlist velocity, creator engagement.",
            "market": "Anchor positioning with 2-3 comps and a why-now argument tied to player demand or platform trends.",
            "business_model": "Show one clean revenue path and publishing upside; avoid multi-model confusion.",
            "team": "Highlight shipped titles, domain expertise, and advisor/publisher support to derisk execution.",
            "ask": "State exact ask, milestone-based use of proceeds, and what success looks like in 12 months.",
        }
        weaknesses = []
        for area, result in scores.items():
            if result.score <= 2:
                weaknesses.append(
                    {
                        "area": area,
                        "score": result.score,
                        "why_weak": result.reasoning,
                        "compensation_narrative": compensation_playbook[area],
                    }
                )
        return weaknesses

    def _narrative_angle(self, studio_data: Dict[str, Any], scores: Dict[str, ScoreResult], audience: str) -> str:
        game_name = studio_data.get("game_name", "the game")
        strongest = sorted(scores.items(), key=lambda x: x[1].score, reverse=True)[:2]
        strength_labels = ", ".join([name for name, _ in strongest])
        if audience == "publisher-first":
            return (
                f"Position {game_name} as a marketable product with clear content hooks, strong production discipline, "
                f"and scalable launch potential. Emphasize {strength_labels} as immediate de-risking signals for portfolio fit."
            )
        if audience == "investor-first":
            return (
                f"Frame {game_name} as a high-upside execution story: focused roadmap, measurable validation, and clear capital efficiency. "
                f"Lead with {strength_labels} to support speed-to-scale confidence."
            )
        return (
            f"Mixed audience strategy: open with undeniable gameplay fantasy, then bridge directly into traction and execution proof. "
            f"Balance publisher confidence (marketability + launch readiness) with investor confidence (scalable upside + milestone discipline). "
            f"Current strength center: {strength_labels}."
        )

    def _key_selling_points(self, studio_data: Dict[str, Any], scores: Dict[str, ScoreResult]) -> List[str]:
        points = [
            "Gameplay-first pitch opening to win attention in under 30 seconds.",
            "Evidence-led traction narrative: only hard signals, no buzzword inflation.",
            "Competitive differentiation framed through player fantasy + execution edge.",
            "Clear milestone ask that maps partner capital to measurable outcomes.",
        ]
        if scores["team"].score >= 4:
            points.append("Team credibility supports delivery risk mitigation.")
        if studio_data.get("development_stage"):
            points.append(f"Development stage clarity: {studio_data['development_stage']}.")
        return points

    def _risks_and_positioning(self, weaknesses: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        if not weaknesses:
            return [
                {
                    "risk": "Overloading slides with detail despite strong fundamentals.",
                    "positioning": "Keep deck to high-signal proof points and use backup slides for depth.",
                }
            ]
        return [
            {
                "risk": f"{item['area']} may reduce confidence in a first-pass review.",
                "positioning": item["compensation_narrative"],
            }
            for item in weaknesses
        ]

    def _slide_priorities(
        self,
        studio_data: Dict[str, Any],
        audience: str,
        weaknesses: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        slides = [
            {"title": "Hook + Gameplay Clarity", "objective": "Show the core loop and player fantasy immediately."},
            {"title": "Traction Signals", "objective": "Present KPIs, wishlists, tests, and external validation."},
            {"title": "Differentiation", "objective": "Explain why this game wins versus direct alternatives."},
            {"title": "Execution Credibility", "objective": "Prove team capability, roadmap realism, and delivery plan."},
            {"title": "Business Model + Market", "objective": "Show monetization logic and market timing for upside."},
            {"title": "The Ask + Next Milestones", "objective": "Make the partnership decision clear and time-bound."},
        ]

        if audience == "publisher-first":
            slides.insert(4, {"title": "Go-To-Market Fit", "objective": "Show channel strategy and portfolio fit for publisher upside."})
        elif audience == "investor-first":
            slides.insert(4, {"title": "Scale Thesis", "objective": "Explain capital efficiency, expansion path, and return logic."})

        if weaknesses:
            slides.append({"title": "Risk Management", "objective": "Address weak spots with explicit mitigation and milestones."})

        slides = slides[:8]
        if len(slides) < 5:
            slides.append({"title": "Team", "objective": "Close confidence gap with founder-market fit."})

        for index, slide in enumerate(slides, start=1):
            slide["slide_number"] = index

        return slides


def generate_pitch_strategy(studio_data: Dict[str, Any], audience: str = "mixed") -> Tuple[Dict[str, Any], str]:
    agent = PitchStrategistAgent(default_audience="mixed")
    strategy = agent.build_strategy(studio_data, audience=audience)
    return strategy, agent.render_pitch_strategy_md(strategy)
