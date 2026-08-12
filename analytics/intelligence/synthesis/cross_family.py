from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from analytics.intelligence.result import Direction
from analytics.intelligence.synthesis.family_aggregator import (
    FamilyEvidence,
)


@dataclass(frozen=True, slots=True)
class CrossFamilySynthesis:
    """Market-level synthesis across independent evidence families."""

    direction: Direction = "NEUTRAL"

    strength: float = 0.0
    confidence: float = 0.0

    bullish_score: float = 0.0
    bearish_score: float = 0.0

    confluence_score: float = 0.0
    conflict_score: float = 0.0

    supporting_families: tuple[str, ...] = ()
    opposing_families: tuple[str, ...] = ()

    family_count: int = 0


class CrossFamilyConfluenceEngine:
    """
    Synthesizes independent evidence families into a market-level thesis.

    This component does not make the final BUY/SELL decision.
    """

    FAMILY_WEIGHTS: dict[str, float] = {
        "GAMMA": 1.00,
        "VOLATILITY": 0.95,
        "OI_FLOW": 0.90,
        "DEALER": 0.90,
        "GREEKS": 0.70,
        "STRUCTURE": 1.00,
        "LIQUIDITY": 0.85,
        "TECHNICAL": 0.75,
        "SCORE": 0.85,
        "HISTORICAL": 0.70,
        "OTHER": 0.50,
    }

    def synthesize(
        self,
        families: Iterable[FamilyEvidence],
    ) -> CrossFamilySynthesis:
        family_items = tuple(families)

        if not family_items:
            return CrossFamilySynthesis()

        bullish_score = 0.0
        bearish_score = 0.0

        supporting: list[str] = []
        opposing: list[str] = []

        weighted_confidence = 0.0
        total_weight = 0.0

        for family in family_items:
            weight = self.FAMILY_WEIGHTS.get(
                family.family,
                self.FAMILY_WEIGHTS["OTHER"],
            )

            contribution = (
                family.strength
                * (family.confidence / 100.0)
                * (family.freshness / 100.0)
                * weight
            )

            total_weight += weight

            weighted_confidence += (
                family.confidence * weight
            )

            if family.direction == "BULLISH":
                bullish_score += contribution
                supporting.append(family.family)

            elif family.direction == "BEARISH":
                bearish_score += contribution
                opposing.append(family.family)

        directional_total = bullish_score + bearish_score

        if directional_total <= 0.0:
            return CrossFamilySynthesis(
                confidence=(
                    weighted_confidence / total_weight
                    if total_weight > 0.0
                    else 0.0
                ),
                bullish_score=bullish_score,
                bearish_score=bearish_score,
                supporting_families=tuple(sorted(supporting)),
                opposing_families=tuple(sorted(opposing)),
                family_count=len(family_items),
            )

        if bullish_score > bearish_score:
            direction: Direction = "BULLISH"
            dominant = bullish_score
            opposing_score = bearish_score

        elif bearish_score > bullish_score:
            direction = "BEARISH"
            dominant = bearish_score
            opposing_score = bullish_score

        else:
            direction = "NEUTRAL"
            dominant = max(
                bullish_score,
                bearish_score,
            )
            opposing_score = min(
                bullish_score,
                bearish_score,
            )

        confluence_score = (
            dominant / directional_total
        ) * 100.0

        conflict_score = (
            opposing_score / directional_total
        ) * 100.0

        strength = (
            dominant / directional_total
        ) * 100.0 if direction != "NEUTRAL" else 0.0

        confidence = (
            weighted_confidence / total_weight
            if total_weight > 0.0
            else 0.0
        )

        return CrossFamilySynthesis(
            direction=direction,
            strength=max(
                0.0,
                min(100.0, strength),
            ),
            confidence=max(
                0.0,
                min(100.0, confidence),
            ),
            bullish_score=bullish_score,
            bearish_score=bearish_score,
            confluence_score=max(
                0.0,
                min(100.0, confluence_score),
            ),
            conflict_score=max(
                0.0,
                min(100.0, conflict_score),
            ),
            supporting_families=tuple(
                sorted(supporting)
            ),
            opposing_families=tuple(
                sorted(opposing)
            ),
            family_count=len(family_items),
        )