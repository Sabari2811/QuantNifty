import pandas as pd


class ATREngine:
    """
    Average True Range (ATR)

    Measures market volatility.

    Returns

        ATR Value
        Volatility State
    """

    def calculate(

        self,

        candles: pd.DataFrame,

        period: int = 14

    ):

        if candles is None:

            return self._empty()

        if len(candles) < period + 1:

            return self._empty()

        df = candles.copy()

        previous_close = df["close"].shift(1)

        tr1 = df["high"] - df["low"]

        tr2 = (df["high"] - previous_close).abs()

        tr3 = (df["low"] - previous_close).abs()

        df["TR"] = pd.concat(

            [tr1, tr2, tr3],

            axis=1

        ).max(axis=1)

        df["ATR"] = (

            df["TR"]

            .rolling(period)

            .mean()

        )

        atr = float(df["ATR"].iloc[-1])

        if atr < 50:

            volatility = "LOW"

        elif atr < 100:

            volatility = "NORMAL"

        elif atr < 200:

            volatility = "HIGH"

        else:

            volatility = "EXTREME"

        return {

            "atr": round(atr, 2),

            "volatility": volatility

        }

    def _empty(self):

        return {

            "atr": 0,

            "volatility": "UNKNOWN"

        }