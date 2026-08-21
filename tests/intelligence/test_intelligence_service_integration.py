from __future__ import annotations

from analytics.intelligence.memory_engine import MarketMemory
from analytics.intelligence.models import TradeIntelligenceRecord

from application.intelligence_service import IntelligenceService


class FakeFeatureExtractor:
    """
    Minimal deterministic FeatureExtractor replacement
    for testing IntelligenceService orchestration.
    """

    def __init__(self, record: TradeIntelligenceRecord):
        self.record = record

    def extract(self, runtime_context):
        return self.record


class FakeEvidence:
    """
    Minimal HistoricalEvidence-compatible object required
    by IntelligenceService.
    """

    recommendation = "BUY"
    confidence_adjustment = 5.0
    explanation = "Historical validation succeeded."


class OrderingEvidenceEngine:
    """
    Verifies that EvidenceEngine.analyze() sees the
    historical memory BEFORE the current record is added.
    """

    def __init__(self, memory: MarketMemory):
        self.memory = memory
        self.observed_size = None
        self.observed_records = None

    def analyze(
        self,
        current: TradeIntelligenceRecord,
        memory: MarketMemory,
    ):
        self.observed_size = memory.size
        self.observed_records = list(memory.records)

        #
        # The current record must NOT already be present.
        #

        assert current not in memory.records

        return FakeEvidence()


def test_intelligence_service_validates_history_before_memory_insert():
    """
    C6.1 regression test.

    Historical evidence must be calculated against the
    pre-existing historical memory.

    The current record must only be inserted AFTER
    EvidenceEngine.analyze() completes.
    """

    memory = MarketMemory()

    historical_record = TradeIntelligenceRecord(
        signal="BUY",
        outcome="WIN",
        pnl=100.0,
    )

    memory.add(
        historical_record
    )

    current_record = TradeIntelligenceRecord(
        signal="BUY",
        confidence=80.0,
    )

    feature_extractor = FakeFeatureExtractor(
        current_record
    )

    evidence_engine = OrderingEvidenceEngine(
        memory
    )

    service = IntelligenceService(
        feature_extractor=feature_extractor,
        market_memory=memory,
        evidence_engine=evidence_engine,
    )

    result = service.analyze(
        runtime_context=object()
    )

    #
    # Evidence engine saw exactly the historical record.
    #

    assert evidence_engine.observed_size == 1

    assert evidence_engine.observed_records == [
        historical_record
    ]

    #
    # Current record was NOT included during historical
    # validation.
    #

    assert current_record not in evidence_engine.observed_records

    #
    # After validation, the current record is stored.
    #

    assert memory.size == 2

    assert memory.records[-1] is current_record

    #
    # Service returned a valid IntelligenceResult.
    #

    assert result.record is current_record

    assert result.evidence is not None

    assert result.recommendation == "BUY"

    assert result.confidence_before == 80.0

    assert result.confidence_after == 85.0

    assert result.explanation == (
        "Historical validation succeeded."
    )


def test_intelligence_service_does_not_add_current_record_when_evidence_is_running():
    """
    Strong ordering check.

    This verifies the memory remains unchanged while
    EvidenceEngine.analyze() is executing.
    """

    memory = MarketMemory()

    historical_record = TradeIntelligenceRecord(
        signal="SELL",
        outcome="LOSS",
        pnl=-50.0,
    )

    memory.add(
        historical_record
    )

    current_record = TradeIntelligenceRecord(
        signal="SELL",
        confidence=60.0,
    )

    feature_extractor = FakeFeatureExtractor(
        current_record
    )

    evidence_engine = OrderingEvidenceEngine(
        memory
    )

    service = IntelligenceService(
        feature_extractor=feature_extractor,
        market_memory=memory,
        evidence_engine=evidence_engine,
    )

    service.analyze(
        runtime_context=object()
    )

    #
    # Evidence saw one historical record, not two.
    #

    assert evidence_engine.observed_size == 1

    #
    # Current record was inserted only after evidence
    # processing completed.
    #

    assert memory.size == 2