import pandas as pd


class EMAEngine:
    """
    EMA Engine

    Calculates:
        EMA9
        EMA20
        EMA50
        EMA200

    Determines trend and EMA20 status.
    """

    def calculate(self, candles: pd.DataFrame):

        if candles is None or candles.empty:
            return self._empty()

        df = candles.copy()

        df["EMA9"] = df["close"].ewm(span=9, adjust=False).mean()
        df["EMA20"] = df["close"].ewm(span=20, adjust=False).mean()
        df["EMA50"] = df["close"].ewm(span=50, adjust=False).mean()
        df["EMA200"] = df["close"].ewm(span=200, adjust=False).mean()

        price = float(df["close"].iloc[-1])

        ema9 = float(df["EMA9"].iloc[-1])
        ema20 = float(df["EMA20"].iloc[-1])
        ema50 = float(df["EMA50"].iloc[-1])
        ema200 = float(df["EMA200"].iloc[-1])

        # ----------------------------------
        # Trend
        # ----------------------------------

        if price > ema20 > ema50 > ema200:
            trend = "STRONG_BULLISH"
        elif price < ema20 < ema50 < ema200:
            trend = "STRONG_BEARISH"
        elif price > ema200:
            trend = "BULLISH"
        elif price < ema200:
            trend = "BEARISH"
        else:
            trend = "SIDEWAYS"

        # ----------------------------------
        # EMA20 Status
        # ----------------------------------

        if price > ema20:
            status = "ABOVE"
        elif price < ema20:
            status = "BELOW"
        else:
            status = "AT_EMA"

        return {

            "ema9": round(ema9, 2),

            "ema20": round(ema20, 2),

            "ema50": round(ema50, 2),

            "ema200": round(ema200, 2),

            "trend": trend,

            "status": status

        }

    def _empty(self):

        return {

            "ema9": 0,

            "ema20": 0,

            "ema50": 0,

            "ema200": 0,

            "trend": "UNKNOWN",

            "status": "UNKNOWN"

        }