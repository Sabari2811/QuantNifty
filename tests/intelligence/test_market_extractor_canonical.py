from analytics.intelligence.extractors.market import MarketExtractor
from analytics.intelligence.models import TradeIntelligenceRecord
from models.market_context import MarketContext


class Context:
    spot = 25000.0
    expiry = "2026-09-10"
    timestamp = ""
    trading_day = "2026-09-03"
    session = "OPEN"
    futures_price = 25010.0
    india_vix = 12.5


def test_market_extractor_prefers_typed_canonical_context_over_analytics():
    ctx = Context()
    ctx.market_context = MarketContext(
        spot=25000.0,
        expected_move={
            "atm_strike": 25000,
            "expected_move": 220,
            "probability": 72,
        },
        market_structure={"structure": "BULLISH"},
        technical={
            "ema": {"trend": "UPTREND"},
            "ad_ratio": {"value": 1.4},
            "rsi": {"rsi": 64},
            "adx": {"adx": 28},
            "vwap": {"distance": 35},
        },
        institutional_score={
            "institutional": {"bias": "BULLISH"}
        },
        probability={"bullish_probability": 78},
        pcr={"oi_pcr": 1.18},
        atr={"atr": 145},
    )

    # Deliberately conflicting compatibility projection.
    ctx.analytics = {
        "expected_move": {
            "atm_strike": 24900,
            "expected_move": 900,
            "probability": 20,
        },
        "market_structure": {"structure": "BEARISH"},
        "technical": {
            "ema": {"trend": "DOWNTREND"},
            "ad_ratio": {"value": 0.4},
            "rsi": {"rsi": 31},
            "adx": {"adx": 12},
            "vwap": {"distance": -80},
        },
        "institutional_score": {
            "institutional": {"bias": "BEARISH"}
        },
        "probability": {"bullish_probability": 22},
        "pcr": {"oi_pcr": 0.71},
        "atr": {"atr": 500},
    }

    record = TradeIntelligenceRecord()
    MarketExtractor().extract(ctx, record)

    assert record.atm_strike == 25000
    assert record.expected_move == 220
    assert record.expected_probability == 72
    assert record.market_structure == "BULLISH"
    assert record.trend == "UPTREND"
    assert record.ad_ratio == 1.4
    assert record.institutional_bias == "BULLISH"
    assert record.probability == 78
    assert record.pcr == 1.18
    assert record.rsi == 64
    assert record.atr == 145
    assert record.adx == 28
    assert record.vwap_distance == 35


def test_market_extractor_keeps_legacy_analytics_fallback():
    ctx = Context()
    ctx.market_context = MarketContext()
    ctx.analytics = {
        "expected_move": {
            "atm_strike": 25000,
            "expected_move": 180,
            "probability": 65,
        },
        "market_structure": {"structure": "BULLISH"},
        "technical": {
            "ema": {"trend": "UPTREND"},
            "ad_ratio": {"value": 1.2},
            "rsi": {"rsi": 61},
            "adx": {"adx": 25},
            "vwap": {"distance": 20},
        },
        "institutional_score": {
            "institutional": {"bias": "BULLISH"}
        },
        "probability": {"bullish_probability": 70},
        "pcr": {"oi_pcr": 1.1},
        "atr": {"atr": 130},
    }

    record = TradeIntelligenceRecord()
    MarketExtractor().extract(ctx, record)

    assert record.atm_strike == 25000
    assert record.expected_move == 180
    assert record.expected_probability == 65
    assert record.market_structure == "BULLISH"
    assert record.trend == "UPTREND"
    assert record.ad_ratio == 1.2
    assert record.institutional_bias == "BULLISH"
    assert record.probability == 70
    assert record.pcr == 1.1
    assert record.rsi == 61
    assert record.atr == 130
    assert record.adx == 25
    assert record.vwap_distance == 20
