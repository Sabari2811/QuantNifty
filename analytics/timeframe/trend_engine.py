import pandas as pd


class TrendEngine:
    """
    Trend Detection Engine

    Determines trend using EMA alignment.
    """

    def analyze(self, candles: pd.DataFrame):

        if candles is None or candles.empty:

            return {

                "trend": "UNKNOWN",

                "strength": 0

            }

        df = candles.copy()

        close = df["close"]

        ema20 = close.ewm(span=20).mean().iloc[-1]
        ema50 = close.ewm(span=50).mean().iloc[-1]
        ema200 = close.ewm(span=200).mean().iloc[-1]

        price = close.iloc[-1]

        bullish = (

            price > ema20 >

            ema50 >

            ema200

        )

        bearish = (

            price < ema20 <

            ema50 <

            ema200

        )

        if bullish:

            trend = "BULLISH"

            strength = 100

        elif bearish:

            trend = "BEARISH"

            strength = 100

        else:

            trend = "SIDEWAYS"

            strength = 50

        return {

            "trend": trend,

            "strength": strength,

            "price": float(price),

            "ema20": float(ema20),

            "ema50": float(ema50),

            "ema200": float(ema200)

        }