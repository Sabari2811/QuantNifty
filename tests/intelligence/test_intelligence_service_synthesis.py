from __future__ import annotations

from datetime import datetime

from analytics.intelligence.evidence_adapter import EvidenceAdapter
from analytics.intelligence.synthesis.family_aggregator import (
    FamilyEvidenceAggregator,
)
from analytics.intelligence.synthesis.orchestration.engine import (
    IntelligenceSynthesisEngine,
)

from application.intelligence_service import (
    IntelligenceService,
)


# ==========================================================
# Fake record
# ==========================================================

class FakeRecord:

    confidence = 70.0

    signal = "WAIT"

    timestamp = datetime.now()


class FakeFeatureExtractor:

    def extract(
        self,
        runtime_context,
    ):

        return FakeRecord()


# ==========================================================
# Fake historical evidence
# ==========================================================

class FakeHistoricalEvidence:

    confidence_adjustment = 5.0

    recommendation = "WAIT"

    explanation = "Historical evidence."


class FakeEvidenceEngine:

    def analyze(
        self,
        record,
        memory,
    ):

        return FakeHistoricalEvidence()


# ==========================================================
# Fake memory
# ==========================================================

class FakeMemory:

    def __init__(self):

        self.records = []

    def add(
        self,
        record,
    ):

        self.records.append(record)


# ==========================================================
# C5 Opportunity contract
# ==========================================================

class FakeContract:

    iv = 18.0

    oi = 100_000

    volume = 50_000

    delta = 0.50


class FakeTrade:

    risk_reward = 2.0

    contract = FakeContract()


class FakeDecision:

    valid = True

    trade = FakeTrade()


# ==========================================================
# Runtime fixture
# ==========================================================

def build_runtime_context():

    from types import SimpleNamespace

    return SimpleNamespace(

        analytics={

            "gamma_flip": {
                "direction": "NEGATIVE_TO_POSITIVE",
            },

            "dealer": {
                "dealer_gamma": "LONG",
            },

            "oi_flow": {
                "summary": {
                    "market_bias": "BULLISH",
                }
            },

            "iv_skew": {
                "iv_bias": "CALLS_EXPENSIVE",
            },

            "probability": {
                "bullish_probability": 75,
                "bearish_probability": 25,
                "confidence": 80,
            },

            "signal": {
                "signal": "BUY CALL",
                "confidence": 80,
            },

            "market_structure": {
                "direction": "BULLISH",
                "strength": 80,
                "confidence": 80,
            },
        },

        decision=FakeDecision(),

        regime={

            "regime": "TRENDING_UP",

            "previous_regime": "RANGE",

            "transition": False,

            "confidence": 80,
        },
    )


# ==========================================================
# C7.3 — C5 synthesis integration
# ==========================================================

def test_service_builds_c5_synthesis():

    memory = FakeMemory()

    service = IntelligenceService(

        feature_extractor=FakeFeatureExtractor(),

        market_memory=memory,

        evidence_engine=FakeEvidenceEngine(),

        evidence_adapter=EvidenceAdapter(),

        family_aggregator=FamilyEvidenceAggregator(),

        synthesis_engine=IntelligenceSynthesisEngine(),

    )

    result = service.analyze(
        build_runtime_context()
    )

    # ======================================================
    # Base result
    # ======================================================

    assert result is not None

    # ======================================================
    # EvidenceAdapter output
    # ======================================================

    assert len(
        result.evidence_items
    ) == 7

    # ======================================================
    # Family aggregation
    # ======================================================

    assert (
        result.evidence_summary.bullish_count
        > 0
    )

    assert (
        result.evidence_summary.correlated_count
        >= 0
    )

    assert (
        0.0
        <= result.evidence_summary.confluence_score
        <= 100.0
    )

    assert (
        0.0
        <= result.evidence_summary.conflict_score
        <= 100.0
    )

    # ======================================================
    # Regime propagation
    # ======================================================

    assert (
        result.regime.regime
        == "TRENDING_UP"
    )

    assert (
        result.regime.previous_regime
        == "RANGE"
    )

    assert (
        result.regime.transition
        is False
    )

    assert (
        result.regime.confidence
        == 80
    )

    # ======================================================
    # Historical confidence
    # ======================================================

    assert (
        result.confidence_before
        == 70.0
    )

    assert (
        result.confidence_after
        == 75.0
    )

    # ======================================================
    # C5 Opportunity Quality
    #
    # R/R       = 30
    # IV        = 20
    # OI        = 20
    # Volume    = 20
    # Delta     = 10
    # ----------------
    # Total     = 100
    # ======================================================

    assert (
        result.opportunity_quality
        == 100.0
    )

    # ======================================================
    # C5 conviction contract
    # ======================================================

    assert (
        0.0
        <= result.conviction
        <= 100.0
    )

    # ======================================================
    # Direction contract
    # ======================================================

    assert result.direction in (
        "BULLISH",
        "BEARISH",
        "NEUTRAL",
    )

    # ======================================================
    # Scenario contract
    # ======================================================

    if result.primary_scenario is not None:

        assert (
            result.primary_scenario.name
        )

        assert (
            0.0
            <= result.primary_scenario.probability
            <= 100.0
        )

    if result.alternative_scenario is not None:

        assert (
            result.alternative_scenario.name
        )

        assert (
            0.0
            <= result.alternative_scenario.probability
            <= 100.0
        )

    # ======================================================
    # Invalidation contract
    # ======================================================

    assert isinstance(
        result.invalidation,
        tuple,
    )

    # ======================================================
    # Reasons contract
    # ======================================================

    assert isinstance(
        result.reasons,
        tuple,
    )

    # ======================================================
    # Contract version
    # ======================================================

    assert (
        result.contract_version
        == "R2-005-A"
    )

    # ======================================================
    # Current record stored once
    # ======================================================

    assert len(
        memory.records
    ) == 1


# ==========================================================
# Historical ordering
# ==========================================================

def test_service_does_not_insert_record_before_historical_evidence():

    class OrderingMemory:

        def __init__(self):

            self.records = []

            self.was_empty_during_analysis = False

        def add(
            self,
            record,
        ):

            self.records.append(record)

        def check_empty(self):

            self.was_empty_during_analysis = (
                len(self.records) == 0
            )

    memory = OrderingMemory()

    class OrderingEvidenceEngine:

        def analyze(
            self,
            record,
            market_memory,
        ):

            market_memory.check_empty()

            return FakeHistoricalEvidence()

    service = IntelligenceService(

        feature_extractor=FakeFeatureExtractor(),

        market_memory=memory,

        evidence_engine=OrderingEvidenceEngine(),

    )

    result = service.analyze(
        build_runtime_context()
    )

    assert result is not None

    assert (
        memory.was_empty_during_analysis
        is True
    )

    assert len(
        memory.records
    ) == 1