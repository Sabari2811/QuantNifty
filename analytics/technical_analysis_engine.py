from analytics.atr_engine import ATREngine
from analytics.ema_engine import EMAEngine
from analytics.rsi_engine import RSIEngine
from analytics.vwap_engine import VWAPEngine
from analytics.adx_engine import ADXEngine


class TechnicalAnalysisEngine:
    """
    Aggregates all technical indicators into one snapshot.
    """

    def __init__(self):

        self.atr = ATREngine()
        self.ema = EMAEngine()
        self.rsi = RSIEngine()
        self.vwap = VWAPEngine()
        self.adx = ADXEngine()

    def analyze(self, candles):

        atr = self.atr.calculate(candles)

        ema = self.ema.calculate(candles)

        rsi = self.rsi.calculate(candles)

        vwap = self.vwap.calculate(candles)

        adx = self.adx.calculate(candles)

        return {

            "atr": atr,

            "ema": ema,

            "rsi": rsi,

            "vwap": vwap,

            "adx": adx

        }