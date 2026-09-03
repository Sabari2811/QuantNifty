from types import SimpleNamespace

from core.runtime_context import RuntimeContext
from engine.replay_engine import ReplayEngine
from models.market_context import MarketContext


EXPECTED_FIELDS = {
    "dealer": {"gamma": "LONG"},
    "dealer_flow": {"delta": 12.5},
    "liquidity": {"score": 71},
    "gamma_flip": {"gamma_flip": 24950},
    "gamma_wall": {"gamma_wall": 25100},
    "oi_flow": {"summary": "CALL_BUILDUP"},
    "iv_skew": {"bias": "PUT"},
    "iv_smile": {"shape": "NORMAL"},
    "expected_move": {"expected_move": 180},
    "max_pain": {"max_pain": 25000},
    "pcr": {"pcr": 1.12},
    "market_structure": {"trend": "BULLISH"},
    "atr": {"atr": 95},
    "volatility": {"regime": "NORMAL"},
    "technical": {"rsi": 62},
    "probability": {"bullish_probability": 68},
    "signal": {"signal": "WAIT"},
    "smart_strike": {"strike": 25000},
    "trade_plan": {"signal": "-"},
    "risk": {"suggested_lots": 0},
    "institutional_score": {"score": 73},
    "market_map": {"spot": 25010},
}


def build_snapshot():
    analytics = dict(EXPECTED_FIELDS)
    analytics["greeks"] = "recorded-greeks"
    return SimpleNamespace(
        timestamp="03-Sep-2026 09:15:00",
        cycle_no=7,
        symbol="NIFTY",
        spot=25010.0,
        option_chain=SimpleNamespace(copy=lambda: "recorded-chain"),
        greeks=SimpleNamespace(copy=lambda: "recorded-greeks"),
        analytics=analytics,
        decision={"signal": "WAIT"},
        explanation={"text": "recorded"},
    )


class FakeReplayProvider:
    def __init__(self, snapshot):
        self.snapshot = snapshot

    def current_snapshot(self):
        return self.snapshot


def test_replay_restores_typed_market_context_from_recorded_analytics():
    snapshot = build_snapshot()
    engine = ReplayEngine(FakeReplayProvider(snapshot))

    ctx = engine.run_cycle()

    assert isinstance(ctx, RuntimeContext)
    assert isinstance(ctx.market_context, MarketContext)
    assert ctx.market_context is not None

    for field_name, expected in EXPECTED_FIELDS.items():
        assert getattr(ctx.market_context, field_name) == expected

    assert ctx.market_context.spot == snapshot.spot
    assert ctx.market_context.greeks == "recorded-greeks"
    assert ctx.analytics is snapshot.analytics


def test_replay_missing_analytics_preserves_typed_context_without_fabrication():
    snapshot = build_snapshot()
    snapshot.analytics = {}
    engine = ReplayEngine(FakeReplayProvider(snapshot))

    ctx = engine.run_cycle()

    assert isinstance(ctx.market_context, MarketContext)
    assert ctx.market_context.dealer == {}
    assert ctx.market_context.signal == {}
    assert ctx.market_context.spot == 0.0
    assert ctx.market_context.greeks is None
