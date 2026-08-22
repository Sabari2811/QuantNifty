from types import SimpleNamespace

from decision.strategy_selector import StrategySelector
from decision.strategies.range_strategy import RangeStrategy
from decision.strategies.trend_strategy import TrendStrategy


def test_trending_market_selects_trend_strategy():

    selector = StrategySelector()

    market = SimpleNamespace(
        regime="TRENDING",
    )

    strategy = selector.select(market)

    assert isinstance(
        strategy,
        TrendStrategy,
    )


def test_range_market_selects_range_strategy():

    selector = StrategySelector()

    market = SimpleNamespace(
        regime="RANGE",
    )

    strategy = selector.select(market)

    assert isinstance(
        strategy,
        RangeStrategy,
    )


def test_unknown_market_regime_preserves_range_fallback():

    selector = StrategySelector()

    market = SimpleNamespace(
        regime="UNKNOWN",
    )

    strategy = selector.select(market)

    assert isinstance(
        strategy,
        RangeStrategy,
    )