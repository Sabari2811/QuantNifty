from __future__ import annotations

from analytics.intelligence.feature_extractor import FeatureExtractor
from analytics.intelligence.memory_engine import MarketMemory
from analytics.intelligence.evidence.evidence_engine import EvidenceEngine
from analytics.intelligence.evidence_adapter import EvidenceAdapter

from analytics.intelligence.synthesis.family_aggregator import (
    FamilyEvidenceAggregator,
)

from analytics.intelligence.synthesis.orchestration.engine import (
    IntelligenceSynthesisEngine,
)

from analytics.intelligence.result import (
    DataQuality,
    EvidenceSummary,
    RegimeState,
    Scenario,
)

from application.models import IntelligenceResult


class IntelligenceService:
    """
    Public API of the Intelligence Layer.

    Flow
    ----
    RuntimeContext
        ↓
    FeatureExtractor
        ↓
    TradeIntelligenceRecord
        ↓
    Historical Evidence
        ↓
    EvidenceAdapter
        ↓
    EvidenceItem[]
        ↓
    FamilyEvidenceAggregator
        ↓
    IntelligenceSynthesisEngine
        ↓
    IntelligenceResult
        ↓
    MarketMemory

    Notes
    -----
    This service orchestrates existing engines.

    It does NOT:
        - calculate indicators
        - alter AnalyticsPipeline output
        - replace DecisionEngine
        - execute trades
    """

    def __init__(
        self,
        feature_extractor: FeatureExtractor,
        market_memory: MarketMemory,
        evidence_engine: EvidenceEngine,
        evidence_adapter: EvidenceAdapter | None = None,
        family_aggregator: FamilyEvidenceAggregator | None = None,
        synthesis_engine: IntelligenceSynthesisEngine | None = None,
    ) -> None:

        self._feature_extractor = feature_extractor
        self._market_memory = market_memory
        self._evidence_engine = evidence_engine
        self._evidence_adapter = evidence_adapter or EvidenceAdapter()
        self._family_aggregator = family_aggregator or FamilyEvidenceAggregator()
        self._synthesis_engine = synthesis_engine or IntelligenceSynthesisEngine()

    @staticmethod
    def _resolve_regime(runtime_context) -> RegimeState:
        regime = getattr(runtime_context, "regime", None)

        if isinstance(regime, RegimeState):
            return regime

        if isinstance(regime, dict):
            return RegimeState(
                regime=str(regime.get("regime", "UNKNOWN") or "UNKNOWN"),
                previous_regime=str(regime.get("previous_regime", "UNKNOWN") or "UNKNOWN"),
                transition=bool(regime.get("transition", False)),
                transition_reason=str(regime.get("transition_reason", "") or ""),
                confidence=float(regime.get("confidence", 0.0) or 0.0),
            )

        if isinstance(regime, str):
            return RegimeState(regime=regime, confidence=0.0)

        if regime is not None and hasattr(regime, "regime"):
            return RegimeState(
                regime=str(getattr(regime, "regime", "UNKNOWN") or "UNKNOWN"),
                previous_regime=str(getattr(regime, "previous_regime", "UNKNOWN") or "UNKNOWN"),
                transition=bool(getattr(regime, "transition", False)),
                transition_reason=str(getattr(regime, "transition_reason", "") or ""),
                confidence=float(getattr(regime, "confidence", 0.0) or 0.0),
            )

        return RegimeState()

    @staticmethod
    def _build_data_quality(runtime_context) -> DataQuality:
        provenance = getattr(runtime_context, "data_provenance", None)

        if provenance is None:
            return DataQuality(
                score=0.0,
                incomplete=True,
                freshness_verified=False,
                reasons=("data_provenance_missing",),
            )

        acquisitions = tuple(
            item
            for item in (provenance.spot, provenance.option_chain, provenance.candles)
            if item is not None
        )

        if not acquisitions:
            return DataQuality(
                score=0.0,
                incomplete=True,
                freshness_verified=False,
                reasons=("no_acquisition_provenance",),
            )

        score = 100.0
        reasons = []
        incomplete = False
        invalid = False
        freshness_verified = True

        for item in acquisitions:
            if not item.complete:
                incomplete = True
                reasons.append(f"incomplete:{item.source}")

            if item.expected_count > 0:
                coverage = item.received_count / item.expected_count
                score = min(score, 100.0 * coverage)

            if not item.freshness_verified:
                freshness_verified = False
                reasons.append(f"freshness_unverified:{item.source}")

            if item.integrity_status == "INVALID":
                invalid = True
                reasons.append(f"integrity_invalid:{item.source}")
            elif item.integrity_status == "SUSPECT":
                reasons.append(f"integrity_suspect:{item.source}")

            reasons.extend(item.reasons)
            reasons.extend(item.integrity_reasons)

        return DataQuality(
            score=max(0.0, min(100.0, score)),
            stale=False,
            incomplete=incomplete,
            invalid=invalid,
            freshness_verified=freshness_verified,
            reasons=tuple(dict.fromkeys(reasons)),
        )

    @staticmethod
    def _build_evidence_summary(families, cross_family) -> EvidenceSummary:
        bullish_count = sum(family.bullish_count for family in families)
        bearish_count = sum(family.bearish_count for family in families)
        neutral_count = sum(1 for family in families if family.direction == "NEUTRAL")
        independent_count = sum(1 for family in families if family.confidence > 0.0)
        correlated_count = max(
            0,
            sum(family.evidence_count for family in families) - independent_count,
        )

        return EvidenceSummary(
            bullish_count=bullish_count,
            bearish_count=bearish_count,
            neutral_count=neutral_count,
            independent_count=independent_count,
            correlated_count=correlated_count,
            confluence_score=max(
                0.0,
                min(100.0, float(getattr(cross_family, "confluence_score", 0.0))),
            ),
            conflict_score=max(
                0.0,
                min(100.0, float(getattr(cross_family, "conflict_score", 0.0))),
            ),
        )

    @staticmethod
    def _build_scenario(scenario) -> Scenario | None:
        if scenario is None:
            return None

        return Scenario(
            name=str(getattr(scenario, "name", "") or ""),
            direction=getattr(scenario, "direction", "NEUTRAL"),
            probability=float(getattr(scenario, "probability", 0.0) or 0.0),
            trigger=str(getattr(scenario, "trigger", "") or ""),
            invalidation=str(getattr(scenario, "invalidation", "") or ""),
            rationale=str(getattr(scenario, "rationale", "") or ""),
        )

    def analyze(self, runtime_context) -> IntelligenceResult:
        record = self._feature_extractor.extract(runtime_context)

        historical_evidence = self._evidence_engine.analyze(
            record,
            self._market_memory,
        )

        evidence_items = self._evidence_adapter.extract(
            getattr(runtime_context, "analytics", {}),
        )

        families = self._family_aggregator.aggregate(evidence_items)
        regime_state = self._resolve_regime(runtime_context)

        decision = getattr(runtime_context, "decision", None)
        synthesis = None

        if decision is not None:
            synthesis = self._synthesis_engine.synthesize(
                families=families,
                decision=decision,
                regime=regime_state.regime,
                regime_confidence=regime_state.confidence,
                transition=regime_state.transition,
            )

        self._market_memory.add(record)

        confidence_before = record.confidence
        confidence_after = max(
            0.0,
            min(100.0, confidence_before + historical_evidence.confidence_adjustment),
        )

        recommendation = (
            historical_evidence.recommendation
            if historical_evidence.recommendation
            else record.signal
        )

        if synthesis is not None:
            cross_family = synthesis.cross_family
            conviction = synthesis.conviction
            opportunity = synthesis.opportunity

            primary_scenario = self._build_scenario(synthesis.scenarios.primary)
            alternative_scenario = self._build_scenario(synthesis.scenarios.alternative)

            direction = getattr(cross_family, "direction", "NEUTRAL")

            # ConvictionResult exposes the canonical score as `conviction`.
            # Do not read a non-existent `score` attribute, which silently
            # converts every real conviction value to the default 0.0.
            conviction_score = float(
                getattr(conviction, "conviction", 0.0) or 0.0
            )
            opportunity_score = float(
                getattr(opportunity, "quality", 0.0) or 0.0
            )
        else:
            direction = "NEUTRAL"
            conviction_score = 0.0
            opportunity_score = 0.0
            primary_scenario = None
            alternative_scenario = None

        data_quality = self._build_data_quality(runtime_context)

        return IntelligenceResult(
            record=record,
            evidence=historical_evidence,
            recommendation=recommendation,
            confidence_before=confidence_before,
            confidence_after=confidence_after,
            explanation=historical_evidence.explanation,
            timestamp=getattr(runtime_context, "timestamp", None),
            direction=direction,
            conviction=conviction_score,
            opportunity_quality=opportunity_score,
            execution_quality=0.0,
            risk_quality=0.0,
            evidence_items=tuple(evidence_items),
            evidence_summary=self._build_evidence_summary(families, cross_family)
            if synthesis is not None
            else EvidenceSummary(),
            regime=regime_state,
            primary_scenario=primary_scenario,
            alternative_scenario=alternative_scenario,
            data_quality=data_quality,
        )
