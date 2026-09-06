from dashboard.components.runtime_card import _display, _status_icon


def test_display_preserves_known_zero_and_false():
    assert _display(0) == 0
    assert _display(False) is False


def test_display_fails_closed_for_missing_and_non_finite():
    assert _display(None) == "UNAVAILABLE"
    assert _display(float("nan")) == "UNAVAILABLE"
    assert _display(float("inf")) == "UNAVAILABLE"


def test_status_icon_handles_unknown_status_without_fabrication():
    assert _status_icon(None) == "⚪"
    assert _status_icon("BLOCKED") == "🔴"
    assert _status_icon("RUNNING") == "🟢"
