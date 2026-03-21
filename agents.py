from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentOutput:
    """Generic output payload for agent steps."""

    name: str
    payload: dict[str, Any]


@dataclass
class PitchStrategistAgent:
    """Builds and refines narrative strategy for the deck."""

    def run(self, structured_summary: dict[str, Any]) -> AgentOutput:
        studio_name = structured_summary.get("studio_name", "Unknown Studio")
        game_name = structured_summary.get("game_name", "Unknown Game")

        strategy = {
            "studio_name": studio_name,
            "game_name": game_name,
            "audience": "mixed",
            "narrative_hook": f"{game_name} is positioned as a high-potential title with execution-ready team.",
            "priority_messages": [
                "Gameplay differentiation",
                "Traction and validation",
                "Clear investment/publishing ask",
            ],
            "weakness_mitigations": [],
        }
        return AgentOutput(name="pitch_strategy", payload=strategy)

    def refine(
        self,
        original_strategy: dict[str, Any],
        qa_weaknesses: list[dict[str, str]],
    ) -> AgentOutput:
        refined = dict(original_strategy)
        mitigations = list(refined.get("weakness_mitigations", []))
        priority_messages = list(refined.get("priority_messages", []))

        for weakness in qa_weaknesses:
            issue = weakness.get("issue", "Unknown weakness")
            suggestion = weakness.get("suggested_fix", "Add stronger evidence and clearer messaging")
            mitigations.append({"issue": issue, "fix": suggestion})
            priority_messages.append(f"Address weakness: {issue}")

        refined["priority_messages"] = priority_messages
        refined["weakness_mitigations"] = mitigations
        refined["refined_from_qa"] = True

        return AgentOutput(name="pitch_strategy", payload=refined)


@dataclass
class SlideWriterAgent:
    """Produces slide outline and markdown deck draft from strategy."""

    max_slides: int = 7

    def build_slides_outline(self, pitch_strategy: dict[str, Any]) -> AgentOutput:
        messages = pitch_strategy.get("priority_messages", [])
        hook = pitch_strategy.get("narrative_hook", "Compelling narrative")
        refined_from_qa = pitch_strategy.get("refined_from_qa", False)

        base_titles = [
            "Cover & Hook",
            "Gameplay & Product",
            "Traction Evidence",
            "Market Opportunity",
            "Business Model",
            "Team",
            "The Ask",
        ]

        outline: list[dict[str, Any]] = []
        for idx, title in enumerate(base_titles[: self.max_slides], start=1):
            message = messages[min(idx - 1, len(messages) - 1)] if messages else hook
            outline.append(
                {
                    "slide_number": idx,
                    "slide_title": title,
                    "slide_objective": f"Support narrative around {title.lower()}.",
                    "key_message": message,
                    "content_blocks": ["headline", "bullet_points", "proof_or_asset"],
                    "suggested_visuals": ["gameplay image", "metric chart"],
                    "source_reference": "validated_source_pack" if refined_from_qa else "",
                    "confidence_level": "medium",
                }
            )

        return AgentOutput(name="slides_outline", payload={"slides": outline})

    def build_draft_deck(
        self,
        pitch_strategy: dict[str, Any],
        slides_outline: dict[str, Any],
    ) -> AgentOutput:
        lines = [
            f"# {pitch_strategy.get('game_name', 'Game')} - Pitch Draft",
            "",
            f"Narrative hook: {pitch_strategy.get('narrative_hook', 'N/A')}",
            "",
        ]

        for slide in slides_outline.get("slides", []):
            lines.extend(
                [
                    f"## Slide {slide['slide_number']}: {slide['slide_title']}",
                    f"- Objective: {slide['slide_objective']}",
                    f"- Key message: {slide['key_message']}",
                    "- Content: headline + concise bullets + one proof point",
                    "",
                ]
            )

        return AgentOutput(name="draft_deck", payload={"markdown": "\n".join(lines)})


@dataclass
class QAAgent:
    """Evaluates pitch quality and returns weaknesses and strengths."""

    required_titles: tuple[str, ...] = (
        "Gameplay",
        "Traction",
        "Team",
        "Ask",
    )

    def run(self, slides_outline: dict[str, Any], draft_deck: dict[str, Any]) -> AgentOutput:
        weaknesses: list[dict[str, str]] = []
        strengths: list[str] = []

        titles = " ".join(slide.get("slide_title", "") for slide in slides_outline.get("slides", []))
        for required in self.required_titles:
            if required.lower() not in titles.lower():
                weaknesses.append(
                    {
                        "issue": f"Missing explicit {required} slide framing",
                        "suggested_fix": f"Add or rename a slide to clearly communicate {required.lower()}.",
                    }
                )
            else:
                strengths.append(f"Contains {required.lower()} coverage")

        if len(draft_deck.get("markdown", "")) < 400:
            weaknesses.append(
                {
                    "issue": "Deck draft is too shallow",
                    "suggested_fix": "Add stronger proof points and audience-specific evidence on each slide.",
                }
            )

        if any(not slide.get("source_reference") for slide in slides_outline.get("slides", [])):
            weaknesses.append(
                {
                    "issue": "Slides are missing source references",
                    "suggested_fix": "Include source_reference for every slide to improve credibility.",
                }
            )

        status = "pass" if not weaknesses else "needs_refinement"
        return AgentOutput(
            name="qa_report",
            payload={
                "status": status,
                "strengths": strengths,
                "weaknesses": weaknesses,
            },
        )


@dataclass
class RefinementLoopOrchestrator:
    """Runs initial pitch generation + QA + refinement loop when needed."""

    strategist: PitchStrategistAgent = field(default_factory=PitchStrategistAgent)
    writer: SlideWriterAgent = field(default_factory=SlideWriterAgent)
    qa_agent: QAAgent = field(default_factory=QAAgent)

    def run(self, structured_summary: dict[str, Any]) -> dict[str, Any]:
        initial_strategy = self.strategist.run(structured_summary).payload
        initial_slides = self.writer.build_slides_outline(initial_strategy).payload
        initial_draft = self.writer.build_draft_deck(initial_strategy, initial_slides).payload
        qa_report = self.qa_agent.run(initial_slides, initial_draft).payload

        result: dict[str, Any] = {
            "initial_version": {
                "pitch_strategy": initial_strategy,
                "slides_outline": initial_slides,
                "draft_deck": initial_draft,
                "qa_report": qa_report,
            },
            "improved_version": None,
        }

        if qa_report.get("weaknesses"):
            improved_strategy = self.strategist.refine(initial_strategy, qa_report["weaknesses"]).payload
            improved_slides = self.writer.build_slides_outline(improved_strategy).payload
            improved_draft = self.writer.build_draft_deck(improved_strategy, improved_slides).payload

            result["improved_version"] = {
                "pitch_strategy": improved_strategy,
                "slides_outline": improved_slides,
                "draft_deck": improved_draft,
                "qa_report": self.qa_agent.run(improved_slides, improved_draft).payload,
            }

        return result
