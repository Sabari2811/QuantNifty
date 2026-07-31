from __future__ import annotations

from analytics.intelligence.feature_extractor import FeatureExtractor
from analytics.intelligence.memory_engine import MarketMemory
from analytics.intelligence.evidence.evidence_engine import EvidenceEngine

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
    MarketMemory
            ↓
    EvidenceEngine
            ↓
    IntelligenceResult

    Notes
    -----
    This class contains NO business rules.

    It only orchestrates existing engines.
    """

    def __init__(
        self,
        feature_extractor: FeatureExtractor,
        market_memory: MarketMemory,
        evidence_engine: EvidenceEngine,
    ):

        self._feature_extractor = feature_extractor

        self._market_memory = market_memory

        self._evidence_engine = evidence_engine

    def analyze(
        self,
        runtime_context,
    ) -> IntelligenceResult:

        #
        # Build market fingerprint
        #

        record = self._feature_extractor.extract(
            runtime_context
        )

        #
        # Store into memory
        #

        self._market_memory.add(
            record
        )

        #
        # Historical evidence
        #

        evidence = self._evidence_engine.analyze(

            record,

            self._market_memory,

        )

        #
        # Final confidence
        #

        confidence_before = record.confidence

        confidence_after = max(

            0.0,

            min(

                100.0,

                confidence_before

                + evidence.confidence_adjustment,

            ),

        )

        #
        # Final recommendation
        #

        recommendation = (

            evidence.recommendation

            if evidence.recommendation

            else record.signal

        )

        return IntelligenceResult(

            record=record,

            evidence=evidence,

            recommendation=recommendation,

            confidence_before=confidence_before,

            confidence_after=confidence_after,

            explanation=evidence.explanation,

        )