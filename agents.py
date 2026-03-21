from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import re


@dataclass
class QAResult:
    checklist: dict[str, bool]
    quality_scoring: dict[str, int]
    demo_day_readiness_score: int
    issues: list[str]
    recommendations: dict[str, list[str]]
    gaps: list[str]


class QAAgent:
    """Evaluates pitch decks for investor/publisher demo day readiness."""

    REQUIRED_CHECKS = {
        "max_8_slides": "Deck has at most 8 slides",
        "has_gameplay_video": "Includes gameplay/video reference",
        "has_metrics_or_success_case": "Includes traction metrics or success case",
        "has_clear_ask": "Includes clear ask",
        "has_team": "Includes team slide/content",
    }

    def evaluate(self, draft_deck_markdown: str) -> QAResult:
        slides = self._split_slides(draft_deck_markdown)
        text = draft_deck_markdown.lower()

        checklist = {
            "max_8_slides": len(slides) <= 8,
            "has_gameplay_video": self._contains_any(text, ["gameplay", "video", "trailer", "demo build"]),
            "has_metrics_or_success_case": self._contains_any(
                text,
                ["wishlist", "retention", "dau", "mau", "conversion", "revenue", "ctr", "kpi", "%"],
            ),
            "has_clear_ask": self._contains_any(text, ["ask", "we are looking for", "raising", "seeking", "looking for"]),
            "has_team": self._contains_any(text, ["team", "founder", "ceo", "cto", "developers"]),
        }

        issues = self._detect_issues(draft_deck_markdown, slides)
        quality_scoring = self._score_quality(draft_deck_markdown, checklist, issues)
        readiness = self._demo_day_readiness(quality_scoring, checklist, issues)

        recommendations = self._recommend(issues, checklist)
        gaps = [label for key, label in self.REQUIRED_CHECKS.items() if not checklist[key]]

        return QAResult(
            checklist=checklist,
            quality_scoring=quality_scoring,
            demo_day_readiness_score=readiness,
            issues=issues,
            recommendations=recommendations,
            gaps=gaps,
        )

    def to_markdown(self, result: QAResult) -> str:
        score_lines = "\n".join(
            [f"- **{k.replace('_', ' ').title()}**: {v}/10" for k, v in result.quality_scoring.items()]
        )

        checklist_lines = "\n".join(
            [
                f"- {'✅' if result.checklist[key] else '❌'} {label}"
                for key, label in self.REQUIRED_CHECKS.items()
            ]
        )

        issues_lines = "\n".join([f"- {item}" for item in result.issues]) if result.issues else "- No major issues found"
        gaps_lines = "\n".join([f"- {gap}" for gap in result.gaps]) if result.gaps else "- No critical information gaps"

        rec_change = (
            "\n".join([f"- {item}" for item in result.recommendations["change"]])
            if result.recommendations["change"]
            else "- No required changes"
        )
        rec_remove = (
            "\n".join([f"- {item}" for item in result.recommendations["remove"]])
            if result.recommendations["remove"]
            else "- Nothing to remove"
        )
        rec_emphasize = (
            "\n".join([f"- {item}" for item in result.recommendations["emphasize"]])
            if result.recommendations["emphasize"]
            else "- No additional emphasis required"
        )

        return f"""# QA Report

## Demo Day Readiness Score
**{result.demo_day_readiness_score}/100**

## Quality Scoring
{score_lines}

## Compliance Checklist
{checklist_lines}

## Detected Issues
{issues_lines}

## Information Gaps
{gaps_lines}

## Actionable Recommendations

### What to change
{rec_change}

### What to remove
{rec_remove}

### What to emphasize
{rec_emphasize}
"""

    def _split_slides(self, markdown: str) -> list[str]:
        slides = re.split(r"(?m)^##\s+", markdown)
        return [s.strip() for s in slides if s.strip()]

    def _contains_any(self, text: str, terms: list[str]) -> bool:
        return any(term in text for term in terms)

    def _detect_issues(self, markdown: str, slides: list[str]) -> list[str]:
        issues: list[str] = []
        lower = markdown.lower()

        if not re.search(r"\b(our game|game concept|core loop|genre|fantasy)\b", lower):
            issues.append("unclear game concept")

        generic_phrases = ["innovative", "next-gen", "revolutionary", "cutting-edge", "disrupt"]
        generic_count = sum(lower.count(phrase) for phrase in generic_phrases)
        if generic_count >= 3:
            issues.append("too generic")

        weak_metric_patterns = [r"\b(many|strong|good|great)\s+(users|traction|growth)\b", r"\b(soon|tbd|coming)\b"]
        has_weak_metrics = any(re.search(pattern, lower) for pattern in weak_metric_patterns)
        has_numeric_metrics = bool(re.search(r"\b\d+[\d,.]*\s*(%|k|m|wishlists|downloads|players|retention|revenue)\b", lower))
        if has_weak_metrics or not has_numeric_metrics:
            issues.append("weak metrics")

        if not re.search(r"\b(ask|seeking|raising|looking for|partner with)\b", lower):
            issues.append("no clear ask")

        words = re.findall(r"\w+", markdown)
        avg_words_per_slide = len(words) / max(1, len(slides))
        if avg_words_per_slide > 140:
            issues.append("too much text")

        return issues

    def _score_quality(self, markdown: str, checklist: dict[str, bool], issues: list[str]) -> dict[str, int]:
        lower = markdown.lower()
        score = {
            "clarity": 8,
            "credibility": 8,
            "traction_strength": 8,
            "differentiation": 8,
            "investor_publisher_appeal": 8,
        }

        if "too much text" in issues or "unclear game concept" in issues:
            score["clarity"] -= 3
        if not checklist["has_clear_ask"]:
            score["clarity"] -= 1

        if "weak metrics" in issues:
            score["credibility"] -= 3
            score["traction_strength"] -= 4

        if "too generic" in issues:
            score["differentiation"] -= 4

        if not self._contains_any(lower, ["publisher", "portfolio", "marketability", "investor", "roi", "upside"]):
            score["investor_publisher_appeal"] -= 3
        if not checklist["has_team"]:
            score["investor_publisher_appeal"] -= 2

        for k in score:
            score[k] = max(1, min(10, score[k]))
        return score

    def _demo_day_readiness(self, quality: dict[str, int], checklist: dict[str, bool], issues: list[str]) -> int:
        weighted_quality = (
            quality["clarity"] * 0.25
            + quality["credibility"] * 0.2
            + quality["traction_strength"] * 0.2
            + quality["differentiation"] * 0.15
            + quality["investor_publisher_appeal"] * 0.2
        )
        checklist_bonus = sum(1 for ok in checklist.values() if ok) / len(checklist) * 20
        penalty = 2 * len(issues)

        score = int(round(weighted_quality * 8 + checklist_bonus - penalty))
        return max(0, min(100, score))

    def _recommend(self, issues: list[str], checklist: dict[str, bool]) -> dict[str, list[str]]:
        rec = {"change": [], "remove": [], "emphasize": []}

        if "unclear game concept" in issues:
            rec["change"].append("Add a one-line game fantasy + genre + target player profile on slide 1-2.")
        if "weak metrics" in issues:
            rec["change"].append("Replace qualitative traction claims with 2-4 numeric KPIs (wishlists, demo retention, conversion, CAGR).")
        if "no clear ask" in issues or not checklist["has_clear_ask"]:
            rec["change"].append("Create a dedicated Ask slide stating amount/partnership sought, use of funds, and expected outcome.")
        if "too much text" in issues:
            rec["remove"].append("Cut long paragraphs; keep each slide to one headline and 3-5 concise bullets.")
        if "too generic" in issues:
            rec["remove"].append("Remove buzzwords (e.g., 'revolutionary', 'next-gen') unless backed by proof.")

        rec["emphasize"].append("Highlight differentiators using concrete comparisons versus closest competitors.")
        rec["emphasize"].append("Show strongest execution proof: shipped milestones, team track record, and gameplay evidence.")
        rec["emphasize"].append("Tailor one section for publishers (marketability/portfolio fit) and one for investors (upside/capital efficiency).")

        return rec
