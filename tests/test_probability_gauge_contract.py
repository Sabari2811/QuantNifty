import math

from dashboard.components.probability_gauge import _normalize_probability


def test_normalize_probability_preserves_known_values():
    assert _normalize_probability(67.5) == 67.5


def test_normalize_probability_preserves_known_zero():
    assert _normalize_probability(0) == 0.0


def test_normalize_probability_returns_none_for_missing_or_invalid():
    assert _normalize_probability(None) is None
    assert _normalize_probability(float("nan")) is None
    assert _normalize_probability(float("inf")) is None
    assert _normalize_probability("not-a-number") is None
