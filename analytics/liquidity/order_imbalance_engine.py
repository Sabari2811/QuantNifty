import pandas as pd


class OrderImbalanceEngine:
    """
    Order Imbalance Engine

    Uses live OI and Volume to estimate buying/selling pressure.
    """

    def analyze(self, greeks_df: pd.DataFrame):

        call_oi = greeks_df["CE_OI"].sum()
        put_oi = greeks_df["PE_OI"].sum()

        call_volume = greeks_df["CE_VOLUME"].sum()
        put_volume = greeks_df["PE_VOLUME"].sum()

        oi_diff = put_oi - call_oi
        volume_diff = put_volume - call_volume

        if oi_diff > 0 and volume_diff > 0:

            pressure = "BUY"

        elif oi_diff < 0 and volume_diff < 0:

            pressure = "SELL"

        else:

            pressure = "NEUTRAL"

        oi_ratio = (
            put_oi / call_oi
            if call_oi > 0 else 0
        )

        volume_ratio = (
            put_volume / call_volume
            if call_volume > 0 else 0
        )

        return {

            "buy_pressure": pressure == "BUY",

            "sell_pressure": pressure == "SELL",

            "pressure": pressure,

            "oi_ratio": round(oi_ratio, 2),

            "volume_ratio": round(volume_ratio, 2),

            "call_oi": int(call_oi),

            "put_oi": int(put_oi),

            "call_volume": int(call_volume),

            "put_volume": int(put_volume)

        }