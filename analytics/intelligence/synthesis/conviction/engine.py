from __future__ import annotations

from dataclasses import dataclass

from analytics.intelligence.result import Direction
from analytics.intelligence.synthesis.cross_family import (
    CrossFamilySynthesis,
)
from analytics.intelligence.synthesis.scenario.engine import (
    ScenarioSet,
)


@dataclass(frozen=True, slots=True)
class ConvictionResult:
    """
    Market conviction derived from synthesized intelligence.

    This component evaluates the quality of an existing directional
    thesis. It does not create the market direction and does not make
    the final BUY/SELL decision.
    """

    direction: Direction = "NEUTRAL"

    conviction: float = 0.0
    quality: float = 0.0
    conflict_level: float = 0.0

    direction_agreement: float = 0.0
    independence_score: float = 0.0
    regime_alignment: float = 0.0
    scenario_alignment: float = 0.0

    explanation: str = ""

    supporting_families: tuple[str, ...] = ()
    opposing_families: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for name in (
            "conviction",
            "quality",
            "conflict_level",
            "direction_agreement",
            "independence_score",
            "regime_alignment",
            "scenario_alignment",
        ):
            value = getattr(self, name)

            if not 0.0 <= value <= 100.0:
                raise ValueError(
                    f"{name} must be between 0 and 100"
                )


class ConvictionEngine:
    """
    Converts cross-family intelligence into market conviction.

    The engine preserves the authoritative direction supplied by
    CrossFamilySynthesis.

    It does not:
        - manufacture direction,
        - reverse direction,
        - select an option,
        - produce BUY/SELL,
        - perform execution planning.
    """

    def evaluate(
        self,
        synthesis: CrossFamilySynthesis,
        scenarios: ScenarioSet,
    ) -> ConvictionResult:
        """
        Evaluate conviction using the current intelligence contracts.

        The current implementation uses:
            - cross-family direction agreement
            - cross-family strength
            - cross-family confidence
            - confluence
            - conflict
            - independent family count
            - regime-adjusted scenario confidence
            - primary scenario alignment

        Liquidity, expected move, dealer alignment, volatility alignment,
        and timeframe alignment are intentionally not fabricated here.
        They will be integrated when their authoritative contracts are
        available.
        """

        direction = synthesis.direction

        if direction == "NEUTRAL":
            return self._neutral_result(
                synthesis=synthesis,
                scenarios=scenarios,
            )

        direction_agreement = self._direction_agreement(
            synthesis
        )

        independence_score = self._independence_score(
            synthesis
        )

        regime_alignment = self._regime_alignment(
            synthesis=synthesis,
            scenarios=scenarios,
        )

        scenario_alignment = self._scenario_alignment(
            synthesis=synthesis,
            scenarios=scenarios,
        )

        conflict_level = self._conflict_level(
            synthesis
        )

        quality = self._quality(
            synthesis=synthesis,
            direction_agreement=direction_agreement,
            independence_score=independence_score,
            regime_alignment=regime_alignment,
            scenario_alignment=scenario_alignment,
        )

        conviction = self._conviction(
            synthesis=synthesis,
            quality=quality,
            conflict_level=conflict_level,
        )

        explanation = self._build_explanation(
            synthesis=synthesis,
            scenarios=scenarios,
            conviction=conviction,
            quality=quality,
            conflict_level=conflict_level,
            direction_agreement=direction_agreement,
            independence_score=independence_score,
            regime_alignment=regime_alignment,
            scenario_alignment=scenario_alignment,
        )

        return ConvictionResult(
            direction=direction,
            conviction=conviction,
            quality=quality,
            conflict_level=conflict_level,
            direction_agreement=direction_agreement,
            independence_score=independence_score,
            regime_alignment=regime_alignment,
            scenario_alignment=scenario_alignment,
            explanation=explanation,
            supporting_families=synthesis.supporting_families,
            opposing_families=synthesis.opposing_families,
        )

    @staticmethod
    def _direction_agreement(
        synthesis: CrossFamilySynthesis,
    ) -> float:
        """
        Direction agreement is represented by confluence.

        A 100 score means all directional evidence supports the
        dominant direction.
        """

        return max(
            0.0,
            min(100.0, synthesis.confluence_score),
        )

    @staticmethod
    def _independence_score(
        synthesis: CrossFamilySynthesis,
    ) -> float:
        """
        Reward multiple independent evidence families.

        One family establishes a baseline. Additional families
        increase confidence with diminishing returns.

        1 family  -> 50
        2 families -> 70
        3 families -> 85
        4+ families -> 100
        """

        count = len(
            synthesis.supporting_families
        )

        if count <= 0:
            return 0.0

        if count == 1:
            return 50.0

        if count == 2:
            return 70.0

        if count == 3:
            return 85.0

        return 100.0

    @staticmethod
    def _regime_alignment(
        synthesis: CrossFamilySynthesis,
        scenarios: ScenarioSet,
    ) -> float:
        """
        Use scenario confidence as the current regime-alignment proxy.

        ScenarioEngine already consumes the regime-adjusted thesis.
        Therefore its resulting confidence is the authoritative
        regime-aware value available to this layer.
        """

        if scenarios.direction == "NEUTRAL":
            return 0.0

        if scenarios.direction != synthesis.direction:
            return 0.0

        return max(
            0.0,
            min(100.0, scenarios.confidence),
        )

    @staticmethod
    def _scenario_alignment(
        synthesis: CrossFamilySynthesis,
        scenarios: ScenarioSet,
    ) -> float:
        """
        Measure whether the primary scenario agrees with the thesis.
        """

        primary = scenarios.primary

        if primary is None:
            return 0.0

        if primary.direction != synthesis.direction:
            return 0.0

        return max(
            0.0,
            min(100.0, primary.probability),
        )

    @staticmethod
    def _conflict_level(
        synthesis: CrossFamilySynthesis,
    ) -> float:
        return max(
            0.0,
            min(100.0, synthesis.conflict_score),
        )

    @staticmethod
    def _quality(
        synthesis: CrossFamilySynthesis,
        direction_agreement: float,
        independence_score: float,
        regime_alignment: float,
        scenario_alignment: float,
    ) -> float:
        """
        Calculate thesis quality.

        Quality deliberately remains separate from conviction.

        Components:
            direction agreement : 30%
            family independence: 20%
            synthesis strength : 20%
            synthesis confidence: 15%
            regime alignment    : 10%
            scenario alignment  : 5%
        """

        quality = (
            direction_agreement * 0.30
            + independence_score * 0.20
            + synthesis.strength * 0.20
            + synthesis.confidence * 0.15
            + regime_alignment * 0.10
            + scenario_alignment * 0.05
        )

        return max(
            0.0,
            min(100.0, round(quality, 6)),
        )

    @staticmethod
    def _conviction(
        synthesis: CrossFamilySynthesis,
        quality: float,
        conflict_level: float,
    ) -> float:
        """
        Convert thesis quality into conviction.

        Conflict is explicitly penalized rather than hidden inside
        the quality score.
        """

        conviction = (
            quality
            * (1.0 - conflict_level / 100.0)
        )

        # Preserve the neutral boundary.
        if synthesis.direction == "NEUTRAL":
            return 0.0

        return max(
            0.0,
            min(100.0, round(conviction, 6)),
        )

    @staticmethod
    def _neutral_result(
        synthesis: CrossFamilySynthesis,
        scenarios: ScenarioSet,
    ) -> ConvictionResult:
        conflict_level = max(
            0.0,
            min(100.0, synthesis.conflict_score),
        )

        explanation = (
            "No directional conviction established because "
            "cross-family evidence is neutral or insufficient."
        )

        return ConvictionResult(
            direction="NEUTRAL",
            conviction=0.0,
            quality=0.0,
            conflict_level=conflict_level,
            direction_agreement=0.0,
            independence_score=0.0,
            regime_alignment=0.0,
            scenario_alignment=0.0,
            explanation=explanation,
            supporting_families=synthesis.supporting_families,
            opposing_families=synthesis.opposing_families,
        )

    @staticmethod
    def _build_explanation(
        synthesis: CrossFamilySynthesis,
        scenarios: ScenarioSet,
        conviction: float,
        quality: float,
        conflict_level: float,
        direction_agreement: float,
        independence_score: float,
        regime_alignment: float,
        scenario_alignment: float,
    ) -> str:
        primary_name = (
            scenarios.primary.name
            if scenarios.primary is not None
            else "none"
        )

        return (
            f"{synthesis.direction} conviction "
            f"{conviction:.2f}/100. "
            f"Quality={quality:.2f}, "
            f"agreement={direction_agreement:.2f}, "
            f"independence={independence_score:.2f}, "
            f"regime_alignment={regime_alignment:.2f}, "
            f"scenario_alignment={scenario_alignment:.2f}, "
            f"conflict={conflict_level:.2f}. "
            f"Primary scenario: {primary_name}."
        )