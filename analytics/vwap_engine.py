import pandas as pd


class VWAPEngine:
    """
    VWAP Engine

    Calculates

        VWAP
        Price Position

    """

    def calculate(self, candles: pd.DataFrame):

        if candles is None or candles.empty:
            return self._empty()

        df = candles.copy()

        typical_price = (

            df["high"]

            + df["low"]

            + df["close"]

        ) / 3

        cumulative_tp_volume = (

            typical_price

            * df["volume"]

        ).cumsum()

        cumulative_volume = (

            df["volume"]

        ).cumsum()

        df["VWAP"] = (

            cumulative_tp_volume

            / cumulative_volume

        )

        price = float(df["close"].iloc[-1])

        vwap = float(df["VWAP"].iloc[-1])

        distance = price - vwap

        if distance > 20:

            position = "ABOVE"

        elif distance < -20:

            position = "BELOW"

        else:

            position = "AT_VWAP"

        return {

            "vwap": round(vwap, 2),

            "price": round(price, 2),

            "distance": round(distance, 2),

            "position": position,

            "status": position

        }

    def _empty(self):

        return {

            "vwap": 0,

            "price": 0,

            "distance": 0,

            "position": "UNKNOWN",

            "status": "UNKNOWN"

        }