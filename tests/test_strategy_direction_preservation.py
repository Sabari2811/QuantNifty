from decision.strategies.trend_strategy import TrendStrategy
from decision.strategies.range_strategy import RangeStrategy


class Market:
    def __init__(self, regime, probability):
        self.regime = regime
        self.probability = probability


def test_trend_strategy_preserves_call_direction():
    market = Market("TRENDING", 80)

    score, reasons = TrendStrategy().adjust(69, market)

    assert score == 79
    assert score > 0
    assert "Trending Market" in reasons


def test_trend_strategy_preserves_put_direction():
    market = Market("TRENDING", 80)

    score, reasons = TrendStrategy().adjust(-69, market)

    assert score == -79
    assert score < 0
    assert "Trending Market" in reasons


def test_trend_strategy_preserves_call_direction_with_high_probability():
    market = Market("TRENDING", 90)

    score, reasons = TrendStrategy().adjust(69, market)

    assert score == 84
    assert score > 0
    assert "Trending Market" in reasons
    assert "Very High Probability" in reasons


def test_trend_strategy_preserves_put_direction_with_high_probability():
    market = Market("TRENDING", 90)

    score, reasons = TrendStrategy().adjust(-69, market)

    assert score == -84
    assert score < 0
    assert "Trending Market" in reasons
    assert "Very High Probability" in reasons


def test_range_strategy_preserves_call_direction():
    market = Market("RANGE", 80)

    score, reasons = RangeStrategy().adjust(69, market)

    assert score == 48
    assert score > 0
    assert "Range Market" in reasons


def test_range_strategy_preserves_put_direction():
    market = Market("RANGE", 80)

    score, reasons = RangeStrategy().adjust(-69, market)

    assert score == -48
    assert score < 0
    assert "Range Market" in reasons