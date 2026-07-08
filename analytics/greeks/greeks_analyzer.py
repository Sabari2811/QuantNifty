import pandas as pd

from config.market_config import NIFTY_LOT_SIZE


class GreeksAnalyzer:

    def __init__(self, lot_size=NIFTY_LOT_SIZE):
        self.lot_size = lot_size

    def enrich(self, df, spot_price):
        """
        Enrich the option chain DataFrame with
        Gamma Exposure (GEX) and
        Delta Exposure (DEX).
        """

        df = df.copy()

        # -------------------------
        # Handle missing values
        # -------------------------

        numeric_cols = [
            "CE_GAMMA",
            "PE_GAMMA",
            "CE_DELTA",
            "PE_DELTA",
            "CE_OI",
            "PE_OI",
        ]

        df[numeric_cols] = df[numeric_cols].fillna(0)

        spot_sq = spot_price ** 2

        # -------------------------
        # Gamma Exposure
        # -------------------------

        df["CE_GEX"] = (
            df["CE_GAMMA"]
            * df["CE_OI"]
            * self.lot_size
            * spot_sq
            * 0.01
        )

        df["PE_GEX"] = (
            df["PE_GAMMA"]
            * df["PE_OI"]
            * self.lot_size
            * spot_sq
            * 0.01
        )

        df["NET_GEX"] = df["CE_GEX"] - df["PE_GEX"]

        # -------------------------
        # Delta Exposure
        # -------------------------

        df["CE_DEX"] = (
            df["CE_DELTA"]
            * df["CE_OI"]
            * self.lot_size
        )

        df["PE_DEX"] = (
            df["PE_DELTA"]
            * df["PE_OI"]
            * self.lot_size
        )

        df["NET_DEX"] = df["CE_DEX"] + df["PE_DEX"]

        return df

    # ==========================================================
    # Summary Methods
    # ==========================================================

    def total_gex(self, df):
        return df["NET_GEX"].sum()

    def total_dex(self, df):
        return df["NET_DEX"].sum()

    def max_gex_strike(self, df):
        return df.loc[df["NET_GEX"].idxmax()]

    def min_gex_strike(self, df):
        return df.loc[df["NET_GEX"].idxmin()]