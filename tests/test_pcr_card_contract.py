from dashboard.components.pcr_card import _display


def test_pcr_display_preserves_known_values():
    assert _display(1.25) == "1.25"
    assert _display(0) == "0.00"


def test_pcr_display_does_not_fabricate_missing_values():
    assert _display(None) == "UNAVAILABLE"
    assert _display(float("nan")) == "UNAVAILABLE"
