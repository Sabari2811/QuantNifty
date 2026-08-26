from datetime import datetime, timezone

from analytics.intelligence.result import DataQuality, IntelligenceResult, RegimeState, Scenario
from dashboard.intelligence_adapter import adapt_intelligence


def _result(**kwargs):
    from analytics.intelligence.evidence.models import HistoricalEvidence
    from analytics.intelligence.models import TradeIntelligenceRecord

    return IntelligenceResult(
        record=TradeIntelligenceRecord(),
        evidence=HistoricalEvidence(),
        recommendation=kwargs.get("recommendation", "WAIT"),
        confidence_before=kwargs.get("confidence_before", 72.0),
        confidence_after=kwargs.get("confidence_after", 61.0),
        explanation="canonical explanation",
        timestamp=datetime(2026, 8, 26, 6, 0, tzinfo=timezone.utc),
        direction="BULLISH",
        conviction=58.0,
        opportunity_quality=64.0,
        execution_quality=52.0,
        risk_quality=71.0,
        regime=RegimeState(regime="RANGE", previous_regime="TRANSITION", transition=True, transition_reason="canonical", confidence=66.0),
        primary_scenario=Scenario(name="Primary", direction="BULLISH", probability=61.0, trigger="24500", invalidation="24300", rationale="canonical"),
        alternative_scenario=Scenario(name="Alternative", direction="BEARISH", probability=39.0),
        data_quality=kwargs.get("data_quality", DataQuality(score=100.0, freshness_verified=False, reasons=("integrity_suspect:INDMoney option quotes",))),
    )


def test_adapter_preserves_canonical_intelligence_values():
    payload = adapt_intelligence(_result())
    assert payload["recommendation"] == "WAIT"
    assert payload["direction"] == "BULLISH"
    assert payload["conviction"] == 58.0
    assert payload["opportunity_quality"] == 64.0
    assert payload["confidence_after"] == 61.0
    assert payload["regime"]["regime"] == "RANGE"
    assert payload["primary_scenario"]["probability"] == 61.0


def test_adapter_keeps_data_quality_independent():
    payload = adapt_intelligence(_result())
    quality = payload["data_quality"]
    assert quality["coverage_score"] == 100.0
    assert quality["integrity_status"] == "SUSPECT"
    assert quality["freshness_status"] == "UNVERIFIED"
