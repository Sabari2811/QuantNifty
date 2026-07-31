import pandas as pd


class RSIEngine:
    """
    Relative Strength Index (RSI)

    Returns:
        RSI value
        Market state
    """

    def calculate(
        self,
        candles: pd.DataFrame,
        period: int = 14
    ):

        if candles is None or len(candles) < period + 1:
            return self._empty()

        df = candles.copy()

        delta = df["close"].diff()

        gain = delta.where(delta > 0, 0.0)

        loss = (-delta).where(delta < 0, 0.0)

        avg_gain = gain.rolling(period).mean()

        avg_loss = loss.rolling(period).mean()

        rs = avg_gain / avg_loss

        rsi = 100 - (100 / (1 + rs))

        value = float(rsi.iloc[-1])

        if value >= 70:
            state = "OVERBOUGHT"

        elif value <= 30:
            state = "OVERSOLD"

        elif value >= 55:
            state = "BULLISH"

        elif value <= 45:
            state = "BEARISH"

        else:
            state = "NEUTRAL"

        return {

            "rsi": round(value, 2),

            "state": state

        }

    def _empty(self):

        return {

            "rsi": 0,

            "state": "UNKNOWN"

        }