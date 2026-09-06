from dashboard.components.signal_card import _display


def test_display_preserves_known_zero():
    assert _display(0, "%") == "0%"


def test_display_returns_unavailable_for_missing_or_non_finite():
    assert _display(None, "%") == "UNAVAILABLE"
    assert _display(float("nan"), "%") == "UNAVAILABLE"
    assert _display(float("inf"), "%") == "UNAVAILABLE"


def test_display_preserves_known_value():
    assert _display(67.5, "%") == "67.5%"
