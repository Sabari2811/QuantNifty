from __future__ import annotations

from dataclasses import dataclass

from analytics.intelligence.result import (
    Direction,
    Regime,
    Scenario,
)
from analytics.intelligence.synthesis.cross_family import (
    CrossFamilySynthesis,
)
from analytics.intelligence.synthesis.regime_adjustment import (
    RegimeAdjustment,
)


@dataclass(frozen=True, slots=True)
class ScenarioSet:
    """Primary and alternative market scenarios."""

    primary: Scenario | None = None
    alternative: Scenario | None = None

    regime: Regime = "UNKNOWN"
    direction: Direction = "NEUTRAL"

    confidence: float = 0.0

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 100.0:
            raise ValueError(
                "scenario confidence must be between 0 and 100"
            )

        if self.primary is not None and self.alternative is not None:
            total = (
                self.primary.probability
                + self.alternative.probability
            )

            if abs(total - 100.0) > 1e-9:
                raise ValueError(
                    "primary and alternative probabilities "
                    "must sum to 100"
                )


class ScenarioEngine:
    """
    Generates plausible market scenarios from an existing thesis.

    This component does not make the final BUY/SELL decision.
    """

    def generate(
        self,
        synthesis: CrossFamilySynthesis,
        regime_adjustment: RegimeAdjustment,
    ) -> ScenarioSet:
        """Generate primary and alternative market scenarios."""

        direction = synthesis.direction
        regime = regime_adjustment.regime

        confidence = max(
            0.0,
            min(
                100.0,
                regime_adjustment.adjusted_confidence,
            ),
        )

        if direction == "NEUTRAL":
            return self._neutral_scenarios(
                regime=regime,
                confidence=confidence,
            )

        primary_probability = self._primary_probability(
            strength=regime_adjustment.adjusted_strength,
            conflict=synthesis.conflict_score,
            confluence=synthesis.confluence_score,
        )

        alternative_probability = (
            100.0 - primary_probability
        )

        if direction == "BULLISH":
            primary = self._bullish_primary(
                probability=primary_probability,
                regime=regime,
            )

            alternative = self._bearish_alternative(
                probability=alternative_probability,
                regime=regime,
            )

        else:
            primary = self._bearish_primary(
                probability=primary_probability,
                regime=regime,
            )

            alternative = self._bullish_alternative(
                probability=alternative_probability,
                regime=regime,
            )

        return ScenarioSet(
            primary=primary,
            alternative=alternative,
            regime=regime,
            direction=direction,
            confidence=confidence,
        )

    @staticmethod
    def _primary_probability(
        strength: float,
        conflict: float,
        confluence: float,
    ) -> float:
        """
        Convert thesis quality into a bounded primary probability.

        Probability is deliberately conservative and does not equal
        conviction directly.
        """

        raw = (
            50.0
            + (strength - 50.0) * 0.35
            + (confluence - 50.0) * 0.15
            - (conflict - 50.0) * 0.20
        )

        return max(
            55.0,
            min(85.0, round(raw, 6)),
        )

    @staticmethod
    def _bullish_primary(
        probability: float,
        regime: Regime,
    ) -> Scenario:
        return Scenario(
            name="Upside continuation",
            direction="BULLISH",
            probability=probability,
            trigger=(
                f"Continuation of bullish structure "
                f"within {regime} regime"
            ),
            invalidation=(
                "Loss of the dominant bullish structure "
                "with confirming opposing evidence"
            ),
            rationale=(
                "Bullish cross-family evidence remains "
                "the dominant market thesis."
            ),
        )

    @staticmethod
    def _bearish_primary(
        probability: float,
        regime: Regime,
    ) -> Scenario:
        return Scenario(
            name="Downside continuation",
            direction="BEARISH",
            probability=probability,
            trigger=(
                f"Continuation of bearish structure "
                f"within {regime} regime"
            ),
            invalidation=(
                "Recovery of the dominant bullish structure "
                "with confirming opposing evidence"
            ),
            rationale=(
                "Bearish cross-family evidence remains "
                "the dominant market thesis."
            ),
        )

    @staticmethod
    def _bearish_alternative(
        probability: float,
        regime: Regime,
    ) -> Scenario:
        return Scenario(
            name="Failed upside thesis",
            direction="BEARISH",
            probability=probability,
            trigger=(
                "Bullish thesis loses structural support "
                "and opposing evidence strengthens"
            ),
            invalidation=(
                f"Renewed bullish continuation within {regime} regime"
            ),
            rationale=(
                "The alternative scenario represents "
                "failure of the dominant bullish thesis."
            ),
        )

    @staticmethod
    def _bullish_alternative(
        probability: float,
        regime: Regime,
    ) -> Scenario:
        return Scenario(
            name="Failed downside thesis",
            direction="BULLISH",
            probability=probability,
            trigger=(
                "Bearish thesis loses structural support "
                "and opposing evidence strengthens"
            ),
            invalidation=(
                f"Renewed bearish continuation within {regime} regime"
            ),
            rationale=(
                "The alternative scenario represents "
                "failure of the dominant bearish thesis."
            ),
        )

    @staticmethod
    def _neutral_scenarios(
        regime: Regime,
        confidence: float,
    ) -> ScenarioSet:
        primary = Scenario(
            name="Balanced market",
            direction="NEUTRAL",
            probability=50.0,
            trigger=(
                "No independent evidence family establishes "
                "a dominant direction"
            ),
            invalidation=(
                "A clear directional cross-family thesis emerges"
            ),
            rationale=(
                "Evidence remains balanced or insufficient "
                "for a directional thesis."
            ),
        )

        alternative = Scenario(
            name="Directional resolution",
            direction="NEUTRAL",
            probability=50.0,
            trigger=(
                "A directional evidence imbalance develops"
            ),
            invalidation=(
                "Evidence returns to balanced conditions"
            ),
            rationale=(
                "The market may resolve directionally, "
                "but the current thesis is neutral."
            ),
        )

        return ScenarioSet(
            primary=primary,
            alternative=alternative,
            regime=regime,
            direction="NEUTRAL",
            confidence=confidence,
        )