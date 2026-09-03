from analytics.market_snapshot.market_snapshot import MarketSnapshot
from decision.decision_engine import DecisionEngine
from models.market_context import MarketContext


def _canonical_context():
    context = MarketContext()
    context.dealer = {"dealer_gamma": "CANONICAL"}
    context.dealer_flow = {"delta": 11}
    context.liquidity = {"score": 22}
    context.pcr = {"bias": "BULLISH"}
    context.expected_move = {"expected_move": 123}
    context.market_structure = {"regime": "TRENDING"}
    context.atr = {"atr": 77}
    context.iv_skew = {"bias": "CALL"}
    context.iv_smile = {"shape": "NORMAL"}
    context.probability = {"prediction_score": 88}
    context.signal = {"signal": "BUY CALL"}
    context.trade_plan = {"recommended_strike": 25000}
    context.max_pain = {"max_pain": 24900}
    context.institutional_score = {"institutional": {"score": 91}}
    context.oi_flow = {"summary": {"call": 10}}
    return context


def test_snapshot_prefers_typed_canonical_context_over_conflicting_analytics():
    canonical = _canonical_context()
    conflicting = {
        "dealer": {"dealer_gamma": "LEGACY"},
        "dealer_flow": {"delta": -11},
        "liquidity": {"score": -22},
        "pcr": {"bias": "BEARISH"},
        "expected_move": {"expected_move": 999},
        "market_structure": {"regime": "RANGE"},
        "atr": {"atr": 999},
        "iv_skew": {"bias": "PUT"},
        "iv_smile": {"shape": "SKEWED"},
        "probability": {"prediction_score": 1},
        "signal": {"signal": "BUY PUT"},
        "trade_plan": {"recommended_strike": 24000},
        "max_pain": {"max_pain": 23000},
        "institutional_score": {"institutional": {"score": 1}},
        "oi_flow": {"summary": {"call": -10}},
    }

    snapshot = MarketSnapshot().save(
        greeks_df=None,
        spot=25000,
        analytics=conflicting,
        market_context=canonical,
    )

    assert snapshot.dealer == canonical.dealer
    assert snapshot.dealer_flow == canonical.dealer_flow
    assert snapshot.liquidity == canonical.liquidity
    assert snapshot.pcr == canonical.pcr
    assert snapshot.expected_move == canonical.expected_move
    assert snapshot.market_structure == canonical.market_structure
    assert snapshot.atr == canonical.atr
    assert snapshot.iv_skew == canonical.iv_skew
    assert snapshot.iv_smile == canonical.iv_smile
    assert snapshot.probability == canonical.probability
    assert snapshot.signal == canonical.signal
    assert snapshot.trade_plan == canonical.trade_plan
    assert snapshot.max_pain == canonical.max_pain
    assert snapshot.institutional == canonical.institutional_score
    assert snapshot.oi_flow == canonical.oi_flow
    assert snapshot.get("signal") == canonical.signal
    assert snapshot.get("dealer") == canonical.dealer


def test_snapshot_without_typed_context_retains_legacy_analytics_behavior():
    analytics = {
        "dealer": {"dealer_gamma": "LEGACY"},
        "signal": {"signal": "BUY PUT"},
        "iv_skew": {"bias": "PUT"},
        "oi_flow": {"summary": {"put": 10}},
    }

    snapshot = MarketSnapshot().save(
        greeks_df=None,
        spot=24000,
        analytics=analytics,
    )

    assert snapshot.market_context is None
    assert snapshot.dealer == analytics["dealer"]
    assert snapshot.signal == analytics["signal"]
    assert snapshot.iv_skew == analytics["iv_skew"]
    assert snapshot.oi == analytics["oi_flow"]
    assert snapshot.get("signal") == analytics["signal"]


def test_decision_engine_direction_uses_canonical_snapshot_signal():
    canonical = _canonical_context()
    conflicting = {
        "signal": {"signal": "BUY PUT"},
    }

    snapshot = MarketSnapshot().save(
        greeks_df=None,
        spot=25000,
        analytics=conflicting,
        market_context=canonical,
    )

    assert DecisionEngine()._extract_direction(snapshot) == "BUY CALL"
