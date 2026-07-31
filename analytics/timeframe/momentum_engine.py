import pandas as pd


class MomentumEngine:
    """
    Momentum Engine

    Uses:

        RSI
        Momentum
    """

    def analyze(self, candles: pd.DataFrame):

        if candles is None or candles.empty:

            return {

                "momentum": "UNKNOWN",

                "strength": 0,

                "rsi": None

            }

        df = candles.copy()

        close = df["close"]

        # ----------------------------------------
        # RSI (14)
        # ----------------------------------------

        delta = close.diff()

        gain = delta.clip(lower=0)

        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(14).mean()

        avg_loss = loss.rolling(14).mean()

        rs = avg_gain / avg_loss.replace(0, 1e-10)

        rsi = 100 - (100 / (1 + rs))

        latest_rsi = float(rsi.iloc[-1])

        # ----------------------------------------
        # Momentum
        # ----------------------------------------

        if latest_rsi >= 60:

            momentum = "BULLISH"

            strength = min(100, int(latest_rsi))

        elif latest_rsi <= 40:

            momentum = "BEARISH"

            strength = min(100, int(100 - latest_rsi))

        else:

            momentum = "NEUTRAL"

            strength = 50

        return {

            "momentum": momentum,

            "strength": strength,

            "rsi": round(latest_rsi, 2)

        }