import pandas as pd


class ATREngine:
    """
    QuantNifty ATR Engine V1

    Temporary ATR estimation.

    Later this engine will calculate
    True ATR from historical candles.
    """

    def analyze(self, greeks_df: pd.DataFrame):

        if greeks_df.empty:

            return {

                "atr": 0,

                "volatility": "UNKNOWN"

            }

        # =====================================
        # ATM Option Premium Approximation
        # =====================================

        atm = greeks_df.iloc[
            len(greeks_df) // 2
        ]

        ce = atm["CE_LTP"]

        pe = atm["PE_LTP"]

        atr = (ce + pe) / 2

        # =====================================
        # Volatility Classification
        # =====================================

        if atr < 80:

            volatility = "LOW"

        elif atr < 150:

            volatility = "NORMAL"

        else:

            volatility = "HIGH"

        return {

            "atr": round(atr, 2),

            "volatility": volatility

        }