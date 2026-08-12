from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from analytics.intelligence.result import Direction, EvidenceItem
from analytics.intelligence.synthesis.independence import (
    EvidenceIndependenceMatrix,
)


@dataclass(frozen=True, slots=True)
class FamilyEvidence:
    """Bounded evidence representing one canonical evidence family."""

    family: str
    direction: Direction = "NEUTRAL"

    strength: float = 0.0
    confidence: float = 0.0
    freshness: float = 100.0

    evidence_count: int = 0
    bullish_count: int = 0
    bearish_count: int = 0

    conflict_score: float = 0.0

    bullish_score: float = 0.0
    bearish_score: float = 0.0


class FamilyEvidenceAggregator:
    """
    Aggregates correlated EvidenceItems into bounded family-level evidence.

    Correlated observations reinforce a family but do not create unlimited
    independent voting power.
    """

    def __init__(
        self,
        matrix: EvidenceIndependenceMatrix | None = None,
    ) -> None:
        self._matrix = matrix or EvidenceIndependenceMatrix()

    def aggregate(
        self,
        items: Iterable[EvidenceItem],
    ) -> tuple[FamilyEvidence, ...]:

        groups: dict[str, list[EvidenceItem]] = {}

        for item in items:
            family = self._matrix.classify(item.feature).name
            groups.setdefault(family, []).append(item)

        results: list[FamilyEvidence] = []

        for family, family_items in groups.items():
            results.append(
                self._aggregate_family(
                    family,
                    family_items,
                )
            )

        return tuple(
            sorted(
                results,
                key=lambda item: item.family,
            )
        )

    @staticmethod
    def _aggregate_family(
        family: str,
        items: list[EvidenceItem],
    ) -> FamilyEvidence:

        bullish_items = [
            item for item in items
            if item.direction == "BULLISH"
        ]

        bearish_items = [
            item for item in items
            if item.direction == "BEARISH"
        ]

        def contribution(item: EvidenceItem) -> float:
            return (
                item.strength
                * (item.confidence / 100.0)
                * (item.freshness / 100.0)
                * item.independence
            )

        bullish_score = sum(
            contribution(item)
            for item in bullish_items
        )

        bearish_score = sum(
            contribution(item)
            for item in bearish_items
        )

        total = bullish_score + bearish_score

        if total <= 0.0:
            direction: Direction = "NEUTRAL"
            strength = 0.0
        elif bullish_score > bearish_score:
            direction = "BULLISH"
            strength = (
                bullish_score / total
            ) * max(
                contribution(item)
                for item in bullish_items
            )
        elif bearish_score > bullish_score:
            direction = "BEARISH"
            strength = (
                bearish_score / total
            ) * max(
                contribution(item)
                for item in bearish_items
            )
        else:
            direction = "NEUTRAL"
            strength = 0.0

        strength = max(0.0, min(100.0, strength))

        weighted_confidence = (
            sum(
                item.confidence * item.independence
                for item in items
            )
            / len(items)
            if items
            else 0.0
        )

        weighted_freshness = (
            sum(
                item.freshness * item.independence
                for item in items
            )
            / len(items)
            if items
            else 0.0
        )

        conflict_score = (
            min(bullish_score, bearish_score)
            / total
            * 100.0
            if total > 0.0
            else 0.0
        )

        return FamilyEvidence(
            family=family,
            direction=direction,
            strength=strength,
            confidence=max(
                0.0,
                min(100.0, weighted_confidence),
            ),
            freshness=max(
                0.0,
                min(100.0, weighted_freshness),
            ),
            evidence_count=len(items),
            bullish_count=len(bullish_items),
            bearish_count=len(bearish_items),
            conflict_score=max(
                0.0,
                min(100.0, conflict_score),
            ),
            bullish_score=bullish_score,
            bearish_score=bearish_score,
        )