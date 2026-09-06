import math

from dashboard.components.kpi_cards import _display_percent


def test_display_percent_preserves_known_zero():
    assert _display_percent(0) == "0%"


def test_display_percent_does_not_fabricate_missing_values():
    assert _display_percent(None) == "—"
    assert _display_percent(float("nan")) == "—"


def test_display_percent_preserves_known_percentage():
    assert _display_percent(67.5) == "67.5%"
