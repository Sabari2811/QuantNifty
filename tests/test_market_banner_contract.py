from dashboard.components.market_banner import _value


def test_value_preserves_known_zero():
    assert _value({"value": 0}, "value") == 0


def test_value_returns_unavailable_for_missing_or_none():
    assert _value({}, "value") == "UNAVAILABLE"
    assert _value({"value": None}, "value") == "UNAVAILABLE"
