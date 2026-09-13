from types import SimpleNamespace

from dashboard.components.trade_cockpit import _brain_status, _regime, _value


def test_trade_cockpit_uses_nifty_decision_context():
    dashboard = SimpleNamespace(
        dealer=SimpleNamespace(market_mode="POSITIVE_GAMMA", support=25000, resistance=25200),
        brain_observation=SimpleNamespace(status="PASS"),
    )
    assert _regime(dashboard) == "POSITIVE GAMMA"
    assert _brain_status(dashboard) == "PASS"
    assert _value({"recommended_strike": 25100}, "recommended_strike") == 25100


def test_trade_cockpit_missing_optional_values_are_safe():
    dashboard = SimpleNamespace(
        dealer=SimpleNamespace(market_mode=None, support=None, resistance=None),
        brain_observation=None,
    )
    assert _regime(dashboard) == "UNKNOWN"
    assert _brain_status(dashboard) == "UNAVAILABLE"
    assert _value({}, "missing") == "—"


def test_trade_cockpit_regime_is_safe_when_dealer_is_missing():
    dashboard = SimpleNamespace(dealer=None)
    assert _regime(dashboard) == "UNKNOWN"
