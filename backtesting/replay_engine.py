from backtesting.models import MarketCandle


class ReplayEngine:
    """
    Sequential historical candle replay.

    Acts like a live market feed.
    """

    def __init__(self, candles):

        self.candles = candles

        self.index = 0

    # ------------------------------------

    def has_next(self):

        return self.index < len(self.candles)

    # ------------------------------------

    def next(self) -> MarketCandle:

        candle = self.candles[self.index]

        self.index += 1

        return candle

    # ------------------------------------

    def reset(self):

        self.index = 0