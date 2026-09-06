from dashboard.components.expected_move_card import _display, _display_number


def test_expected_move_display_preserves_known_values():
    assert _display_number(25123.456) == "25,123.46"
    assert _display_number(123.456, prefix="± ") == "± 123.46"
    assert _display("IV") == "IV"


def test_expected_move_display_does_not_fabricate_missing_or_nonfinite_values():
    assert _display_number(None) == "UNAVAILABLE"
    assert _display_number(float("nan")) == "UNAVAILABLE"
    assert _display_number(float("inf")) == "UNAVAILABLE"
    assert _display(None) == "UNAVAILABLE"
