from decision.strategies.trend_strategy import TrendStrategy
from decision.strategies.range_strategy import RangeStrategy


class StrategySelector:
    """
    Selects the appropriate trading strategy
    based on the current MarketContext.
    """

    def __init__(self):

        self.trend = TrendStrategy()

        self.range = RangeStrategy()

    def select(self, market):

        if market.regime == "TRENDING":

            return self.trend

        elif market.regime == "RANGE":

            return self.range

        #
        # Future
        #

        # BREAKOUT

        # REVERSAL

        return self.range