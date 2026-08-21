from __future__ import annotations

from dataclasses import dataclass

from analytics.intelligence.synthesis.cross_family import (
    CrossFamilyConfluenceEngine,
    CrossFamilySynthesis,
)

from analytics.intelligence.synthesis.regime_adjustment import (
    RegimeAwareIntelligence,
    RegimeAdjustment,
)

from analytics.intelligence.synthesis.scenario.engine import (
    ScenarioEngine,
    ScenarioSet,
)

from analytics.intelligence.synthesis.conviction.engine import (
    ConvictionEngine,
    ConvictionResult,
)

from analytics.intelligence.synthesis.opportunity.engine import (
    OpportunityQuality,
    OpportunityQualityEngine,
)


@dataclass(frozen=True, slots=True)
class IntelligenceSynthesis:
    """
    Complete deterministic synthesis produced by C5.

    This object contains the outputs of every synthesis stage.

    It does NOT make the final BUY/SELL decision.
    """

    cross_family: CrossFamilySynthesis

    regime: RegimeAdjustment

    scenarios: ScenarioSet

    conviction: ConvictionResult

    opportunity: OpportunityQuality


class IntelligenceSynthesisEngine:
    """
    Orchestrates the Intelligence synthesis pipeline.

    Responsibilities
    ----------------
    1. Cross-family synthesis
    2. Regime adjustment
    3. Scenario generation
    4. Conviction evaluation
    5. Opportunity quality evaluation

    This class contains no independent trading rules.

    It only coordinates authoritative engines.
    """

    def __init__(
        self,
        cross_family_engine: CrossFamilyConfluenceEngine | None = None,
        regime_engine: RegimeAwareIntelligence | None = None,
        scenario_engine: ScenarioEngine | None = None,
        conviction_engine: ConvictionEngine | None = None,
        opportunity_engine: OpportunityQualityEngine | None = None,
    ) -> None:

        self.cross_family_engine = (
            cross_family_engine
            or CrossFamilyConfluenceEngine()
        )

        self.regime_engine = (
            regime_engine
            or RegimeAwareIntelligence()
        )

        self.scenario_engine = (
            scenario_engine
            or ScenarioEngine()
        )

        self.conviction_engine = (
            conviction_engine
            or ConvictionEngine()
        )

        self.opportunity_engine = (
            opportunity_engine
            or OpportunityQualityEngine()
        )

    def synthesize(
        self,
        families,
        decision,
        regime,
        regime_confidence: float = 100.0,
        transition: bool = False,
    ) -> IntelligenceSynthesis:
        """
        Execute the complete synthesis pipeline.

        Parameters
        ----------
        families:
            Iterable[FamilyEvidence].

        decision:
            Existing Decision object used only by the
            OpportunityQualityEngine.

        regime:
            Current authoritative market regime.

        regime_confidence:
            Confidence in the supplied regime.

        transition:
            Whether the market is currently transitioning
            between regimes.
        """

        cross_family = self.cross_family_engine.synthesize(
            families
        )

        regime_adjustment = self.regime_engine.adjust(
            synthesis=cross_family,
            regime=regime,
            regime_confidence=regime_confidence,
            transition=transition,
        )

        scenarios = self.scenario_engine.generate(
            synthesis=cross_family,
            regime_adjustment=regime_adjustment,
        )

        conviction = self.conviction_engine.evaluate(
            synthesis=cross_family,
            scenarios=scenarios,
        )

        opportunity = self.opportunity_engine.evaluate(
            decision
        )

        return IntelligenceSynthesis(
            cross_family=cross_family,
            regime=regime_adjustment,
            scenarios=scenarios,
            conviction=conviction,
            opportunity=opportunity,
        )