import pandas as pd
import numpy as np


class ADXEngine:
    """
    Average Directional Index (ADX)

    Returns:
        ADX
        Trend Strength
    """

    def calculate(
        self,
        candles: pd.DataFrame,
        period: int = 14
    ):

        if candles is None or len(candles) < period + 1:
            return self._empty()

        df = candles.copy()

        df["up_move"] = df["high"].diff()
        df["down_move"] = -df["low"].diff()

        df["+DM"] = np.where(
            (df["up_move"] > df["down_move"]) &
            (df["up_move"] > 0),
            df["up_move"],
            0
        )

        df["-DM"] = np.where(
            (df["down_move"] > df["up_move"]) &
            (df["down_move"] > 0),
            df["down_move"],
            0
        )

        prev_close = df["close"].shift(1)

        tr = pd.concat(
            [
                df["high"] - df["low"],
                (df["high"] - prev_close).abs(),
                (df["low"] - prev_close).abs()
            ],
            axis=1
        ).max(axis=1)

        atr = tr.rolling(period).mean()

        plus_di = (
            100 *
            (df["+DM"].rolling(period).mean() / atr)
        )

        minus_di = (
            100 *
            (df["-DM"].rolling(period).mean() / atr)
        )

        dx = (
            (
                (plus_di - minus_di).abs()
            ) /
            (
                plus_di + minus_di
            )
        ) * 100

        adx = dx.rolling(period).mean()

        value = float(adx.iloc[-1])

        if value < 20:

            strength = "WEAK"

        elif value < 40:

            strength = "NORMAL"

        elif value < 60:

            strength = "STRONG"

        else:

            strength = "VERY_STRONG"

        return {

            "adx": round(value, 2),

            "strength": strength

        }

    def _empty(self):

        return {

            "adx": 0,

            "strength": "UNKNOWN"

        }