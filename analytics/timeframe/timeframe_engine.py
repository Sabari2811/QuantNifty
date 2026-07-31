from analytics.timeframe.trend_engine import TrendEngine
from analytics.timeframe.momentum_engine import MomentumEngine


class TimeframeEngine:
    """
    Master Timeframe Engine

    Combines:

        Trend
        Momentum

    Returns a single timeframe decision.
    """

    def __init__(self):

        self.trend = TrendEngine()

        self.momentum = MomentumEngine()

    def analyze(

        self,

        candles

    ):

        trend = self.trend.analyze(candles)

        momentum = self.momentum.analyze(candles)

        bullish = 0
        bearish = 0

        # ----------------------------------------
        # Trend
        # ----------------------------------------

        if trend["trend"] == "BULLISH":

            bullish += 1

        elif trend["trend"] == "BEARISH":

            bearish += 1

        # ----------------------------------------
        # Momentum
        # ----------------------------------------

        if momentum["momentum"] == "BULLISH":

            bullish += 1

        elif momentum["momentum"] == "BEARISH":

            bearish += 1

        # ----------------------------------------
        # Final Decision
        # ----------------------------------------

        if bullish == 2:

            direction = "BULLISH"

            confidence = 100

        elif bearish == 2:

            direction = "BEARISH"

            confidence = 100

        elif bullish > bearish:

            direction = "BULLISH"

            confidence = 70

        elif bearish > bullish:

            direction = "BEARISH"

            confidence = 70

        else:

            direction = "NEUTRAL"

            confidence = 50

        return {

            "direction": direction,

            "confidence": confidence,

            "trend": trend,

            "momentum": momentum

        }