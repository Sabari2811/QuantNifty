from dashboard.components.max_pain_card import _display


def test_max_pain_display_preserves_known_values():
    assert _display(25000, decimals=0) == "25,000"
    assert _display(1500000, decimals=0) == "1,500,000"


def test_max_pain_display_does_not_fabricate_missing_values():
    assert _display(None, decimals=0) == "UNAVAILABLE"


def test_max_pain_display_preserves_real_zero():
    assert _display(0, decimals=0) == "0"
