from types import SimpleNamespace

from application.intelligence_service import IntelligenceService


class _FeatureExtractor:
    def extract(self, _context):
        return SimpleNamespace(
            timestamp=None,
            confidence=40.0,
            signal="WAIT",
        )


class _MarketMemory:
    def add(self, _record):
        pass


class _EvidenceEngine:
    def analyze(self, _record, _memory):
        return SimpleNamespace(
            recommendation="",
            confidence_adjustment=0.0,
            explanation="",
        )


class _EvidenceAdapter:
    def extract(self, _analytics):
        return ()


class _FamilyAggregator:
    def aggregate(self, _items):
        return ()


class _SynthesisEngine:
    def synthesize(self, **_kwargs):
        return SimpleNamespace(
            cross_family=SimpleNamespace(direction="BULLISH"),
            conviction=SimpleNamespace(conviction=72.5),
            opportunity=SimpleNamespace(score=0.0),
            scenarios=SimpleNamespace(
                primary=SimpleNamespace(
                    name="Upside continuation",
                    direction="BULLISH",
                    probability=55.0,
                    trigger="continuation",
                    invalidation="loss of structure",
                    rationale="",
                ),
                alternative=SimpleNamespace(
                    name="Failed upside thesis",
                    direction="BEARISH",
                    probability=45.0,
                    trigger="failure",
                    invalidation="",
                    rationale="",
                ),
            ),
        )


def _context():
    acquisition = SimpleNamespace(
        complete=True,
        source="test",
        expected_count=1,
        received_count=1,
        freshness_verified=False,
        reasons=(),
    )

    return SimpleNamespace(
        analytics={},
        decision=object(),
        regime=SimpleNamespace(
            regime="RANGE",
            previous_regime="RANGE",
            transition=False,
            transition_reason="",
            confidence=0.0,
        ),
        data_provenance=SimpleNamespace(
            spot=acquisition,
            option_chain=acquisition,
            candles=acquisition,
        ),
    )


def test_intelligence_service_preserves_conviction_result_value():
    service = IntelligenceService(
        feature_extractor=_FeatureExtractor(),
        market_memory=_MarketMemory(),
        evidence_engine=_EvidenceEngine(),
        evidence_adapter=_EvidenceAdapter(),
        family_aggregator=_FamilyAggregator(),
        synthesis_engine=_SynthesisEngine(),
    )

    result = service.analyze(_context())

    assert result.direction == "BULLISH"
    assert result.conviction == 72.5
    assert result.opportunity_quality == 0.0
    assert result.primary_scenario.probability == 55.0
