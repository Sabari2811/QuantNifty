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
    # Gamma flip is a regime/level transition and is deliberately
    # excluded from directional evidence. The six directional
    # observations are dealer gamma, OI flow, IV skew, probability,
    # signal, and market structure.

    assert len(
        result.evidence_items
    ) == 6

    assert {
        item.feature
        for item in result.evidence_items
    } == {
        "dealer_gamma",
        "oi_flow_market_bias",
        "iv_skew",
        "probability",
        "signal",
        "market_structure",
    }

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
