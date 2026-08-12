from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from analytics.intelligence.result import (
    Direction,
    EvidenceItem,
    EvidenceSummary,
)


@dataclass(frozen=True, slots=True)
class EvidenceSynthesis:
    """Normalized evidence plus confluence/conflict statistics."""

    items: tuple[EvidenceItem, ...]
    summary: EvidenceSummary


class EvidenceSynthesisEngine:
    """
    Converts heterogeneous intelligence evidence into a normalized,
    correlation-aware evidence set.

    This engine does NOT make a BUY/SELL decision.
    """

    def synthesize(
        self,
        items: Iterable[EvidenceItem],
    ) -> EvidenceSynthesis:

        normalized = tuple(
            self._normalize(item)
            for item in items
        )

        bullish = sum(
            1 for item in normalized
            if item.direction == "BULLISH"
        )

        bearish = sum(
            1 for item in normalized
            if item.direction == "BEARISH"
        )

        neutral = sum(
            1 for item in normalized
            if item.direction == "NEUTRAL"
        )

        independent = sum(
            1 for item in normalized
            if item.independence >= 0.75
        )

        correlated = len(normalized) - independent

        bullish_strength = sum(
            item.strength * item.confidence / 100.0
            for item in normalized
            if item.direction == "BULLISH"
        )

        bearish_strength = sum(
            item.strength * item.confidence / 100.0
            for item in normalized
            if item.direction == "BEARISH"
        )

        total_directional = (
            bullish_strength + bearish_strength
        )

        if total_directional > 0:
            confluence_score = (
                max(bullish_strength, bearish_strength)
                / total_directional
                * 100.0
            )

            conflict_score = (
                min(bullish_strength, bearish_strength)
                / total_directional
                * 100.0
            )
        else:
            confluence_score = 0.0
            conflict_score = 0.0

        summary = EvidenceSummary(
            bullish_count=bullish,
            bearish_count=bearish,
            neutral_count=neutral,
            independent_count=independent,
            correlated_count=correlated,
            confluence_score=confluence_score,
            conflict_score=conflict_score,
        )

        return EvidenceSynthesis(
            items=normalized,
            summary=summary,
        )

    @staticmethod
    def _normalize(item: EvidenceItem) -> EvidenceItem:
        """
        Normalize evidence values while preserving the original
        evidence identity and rationale.
        """

        direction: Direction = item.direction

        return EvidenceItem(
            source_family=item.source_family.strip(),
            feature=item.feature.strip(),
            direction=direction,
            strength=max(0.0, min(100.0, item.strength)),
            confidence=max(0.0, min(100.0, item.confidence)),
            freshness=max(0.0, min(100.0, item.freshness)),
            independence=max(0.0, min(1.0, item.independence)),
            reason=item.reason.strip(),
        )
