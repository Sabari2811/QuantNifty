from __future__ import annotations

from analytics.intelligence.evidence_adapter import EvidenceAdapter
from models.market_context import MarketContext


def build_analytics():
    return {
        "gamma_flip": {"direction": "NEGATIVE_TO_POSITIVE", "gamma_flip": 25000},
        "dealer": {"dealer_gamma": "LONG"},
        "oi_flow": {"summary": {"market_bias": "BULLISH"}},
        "iv_skew": {"iv_bias": "CALLS_EXPENSIVE"},
        "probability": {"bullish_probability": 75, "bearish_probability": 25, "confidence": 50},
        "signal": {"signal": "BUY CALL", "confidence": 50},
        "market_structure": {"direction": "BULLISH", "strength": 80, "confidence": 75},
    }


def test_adapter_accepts_analytics_pipeline_result():
    assert len(EvidenceAdapter().extract(build_analytics())) == 6


def test_adapter_extracts_expected_features():
    items = EvidenceAdapter().extract(build_analytics())
    assert {item.feature for item in items} == {
        "dealer_gamma", "oi_flow_market_bias", "iv_skew", "probability", "signal", "market_structure"
    }


def test_gamma_flip_is_not_converted_to_directional_evidence():
    analytics = build_analytics()
    analytics["dealer"] = {"dealer_gamma": "SHORT"}
    analytics["oi_flow"] = {"summary": {"market_bias": "BEARISH"}}
    analytics["iv_skew"] = {"iv_bias": "PUTS_EXPENSIVE"}
    analytics["probability"] = {"bullish_probability": 25, "bearish_probability": 75, "confidence": 50}
    analytics["signal"] = {"signal": "BUY PUT", "confidence": 50}
    analytics["market_structure"] = {"direction": "BEARISH", "strength": 80, "confidence": 75}
    items = EvidenceAdapter().extract(analytics)
    assert "gamma_flip" not in {item.feature for item in items}
    assert all(item.direction == "BEARISH" for item in items)


def test_adapter_preserves_bullish_direction():
    items = EvidenceAdapter().extract(build_analytics())
    assert all(item.direction == "BULLISH" for item in items)


def test_adapter_preserves_bearish_direction():
    analytics = build_analytics()
    analytics["gamma_flip"] = {"direction": "POSITIVE_TO_NEGATIVE"}
    analytics["dealer"] = {"dealer_gamma": "SHORT"}
    analytics["oi_flow"] = {"summary": {"market_bias": "BEARISH"}}
    analytics["iv_skew"] = {"iv_bias": "PUTS_EXPENSIVE"}
    analytics["probability"] = {"bullish_probability": 25, "bearish_probability": 75, "confidence": 50}
    analytics["signal"] = {"signal": "BUY PUT", "confidence": 50}
    analytics["market_structure"] = {"direction": "BEARISH", "strength": 80, "confidence": 75}
    items = EvidenceAdapter().extract(analytics)
    assert all(item.direction == "BEARISH" for item in items)


def test_adapter_ignores_neutral_sources():
    analytics = {
        "gamma_flip": {"direction": None},
        "dealer": {"dealer_gamma": "UNKNOWN"},
        "oi_flow": {"summary": {"market_bias": "NEUTRAL"}},
        "iv_skew": {"iv_bias": "UNKNOWN"},
        "probability": {"bullish_probability": 50, "bearish_probability": 50, "confidence": 0},
        "signal": {"signal": "WAIT", "confidence": 0},
        "market_structure": {"direction": "NEUTRAL"},
    }
    assert EvidenceAdapter().extract(analytics) == ()


def test_adapter_handles_invalid_input():
    adapter = EvidenceAdapter()
    assert adapter.extract(None) == ()
    assert adapter.extract([]) == ()
    assert adapter.extract("invalid") == ()


def test_adapter_reads_canonical_market_context_instead_of_legacy_projection():
    """Canonical typed context must be sufficient and authoritative."""
    context = MarketContext(
        dealer={"dealer_gamma": "LONG"},
        oi_flow={"summary": {"market_bias": "BULLISH"}},
        iv_skew={"iv_bias": "CALLS_EXPENSIVE"},
        probability={"bullish_probability": 75, "bearish_probability": 25, "confidence": 50},
        signal={"signal": "BUY CALL", "confidence": 50},
        market_structure={"direction": "BULLISH", "strength": 80, "confidence": 75},
    )
    items = EvidenceAdapter().extract(context)
    assert len(items) == 6
    assert {item.direction for item in items} == {"BULLISH"}
