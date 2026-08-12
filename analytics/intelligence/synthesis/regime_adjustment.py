from __future__ import annotations

from dataclasses import dataclass

from analytics.intelligence.result import Direction, Regime
from analytics.intelligence.synthesis.cross_family import (
    CrossFamilySynthesis,
)


@dataclass(frozen=True, slots=True)
class RegimeAdjustment:
    """Regime-dependent interpretation of a market thesis."""

    regime: Regime = "UNKNOWN"

    direction: Direction = "NEUTRAL"

    base_strength: float = 0.0
    adjusted_strength: float = 0.0

    base_confidence: float = 0.0
    adjusted_confidence: float = 0.0

    regime_multiplier: float = 1.0
    transition_penalty: float = 0.0

    reason: str = ""


class RegimeAwareIntelligence:
    """
    Adjusts an existing market thesis according to market regime.

    This component does not create a directional signal and does not
    produce the final BUY/SELL decision.
    """

    REGIME_MULTIPLIERS: dict[Regime, float] = {
        "TRENDING_UP": 1.10,
        "TRENDING_DOWN": 1.10,
        "RANGE": 0.80,
        "BREAKOUT": 1.05,
        "BREAKDOWN": 1.05,
        "TRANSITION": 0.60,
        "HIGH_VOLATILITY": 0.75,
        "LOW_VOLATILITY": 0.90,
        "UNKNOWN": 0.70,
    }

    def adjust(
        self,
        synthesis: CrossFamilySynthesis,
        regime: Regime,
        regime_confidence: float = 100.0,
        transition: bool = False,
    ) -> RegimeAdjustment:
        """Apply regime-aware adjustment to a market synthesis."""

        if not 0.0 <= regime_confidence <= 100.0:
            raise ValueError(
                "regime_confidence must be between 0 and 100"
            )

        multiplier = self.REGIME_MULTIPLIERS.get(
            regime,
            self.REGIME_MULTIPLIERS["UNKNOWN"],
        )

        transition_penalty = 0.20 if transition else 0.0

        effective_multiplier = (
            multiplier
            * (regime_confidence / 100.0)
        )

        if transition:
            effective_multiplier *= (
                1.0 - transition_penalty
            )

        adjusted_strength = round(
            synthesis.strength * effective_multiplier,
            10,
        )

        adjusted_confidence = round(
            synthesis.confidence * effective_multiplier,
            10,
        )

        adjusted_strength = max(
            0.0,
            min(100.0, adjusted_strength),
        )

        adjusted_confidence = max(
            0.0,
            min(100.0, adjusted_confidence),
        )

        reason = (
            f"{regime} regime applied with "
            f"{multiplier:.2f}x multiplier"
        )

        if transition:
            reason += "; transition penalty applied"

        return RegimeAdjustment(
            regime=regime,
            direction=synthesis.direction,
            base_strength=synthesis.strength,
            adjusted_strength=adjusted_strength,
            base_confidence=synthesis.confidence,
            adjusted_confidence=adjusted_confidence,
            regime_multiplier=multiplier,
            transition_penalty=transition_penalty,
            reason=reason,
        )