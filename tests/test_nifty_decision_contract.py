from analytics.market_snapshot.market_snapshot import MarketSnapshot
from decision.constants import Signal
from decision.decision_engine import DecisionEngine


def _snapshot(signal=None):
    analytics = {
        "signal": {"signal": signal} if signal is not None else {},
        "dealer": {"dealer_gamma": "LONG", "gamma_flip": 24200, "gamma_wall": 24300},
        "dealer_flow": {},
        "liquidity": {},
        "market_structure": {},
        "pcr": {},
        "expected_move": {},
        "iv_skew": {},
        "iv_smile": {},
        "atr": {},
        "institutional_score": {"institutional": {"score": 80}},
    }
    return MarketSnapshot().save(greeks_df=None, spot=24300, analytics=analytics)


def test_missing_nifty_signal_is_wait_not_score_derived_trade():
    decision = DecisionEngine().build(_snapshot())
    assert decision.signal.name == Signal.WAIT.value


def test_nifty_direction_is_authoritative():
    decision = DecisionEngine().build(_snapshot(Signal.BUY_PUT.value))
    assert decision.signal.name == Signal.BUY_PUT.value
    assert decision.authoritative_signal == Signal.BUY_PUT.value


def test_non_nifty_snapshot_is_rejected():
    snapshot = _snapshot(Signal.BUY_CALL.value)
    snapshot.market_context = type("Context", (), {"symbol": "BANKNIFTY"})()
    try:
        DecisionEngine().build(snapshot)
    except ValueError as exc:
        assert str(exc).startswith("NIFTY_ONLY_SYMBOL_REQUIRED")
    else:
        raise AssertionError("Non-NIFTY snapshot must be rejected")
