import pandas as pd


class DeltaExposureEngine:
    """
    Delta Exposure (DEX)

    DEX = Delta × OI × Spot × Lot Size

    Positive DEX
        Dealers long delta

    Negative DEX
        Dealers short delta
    """

    def __init__(self, lot_size=75):
        self.lot_size = lot_size

    def calculate(self, df: pd.DataFrame, spot_price: float):

        df = df.copy()

        # -----------------------
        # Call DEX
        # -----------------------

        df["CALL_DEX"] = (
            df["CE_DELTA"]
            * df["CE_OI"]
            * spot_price
            * self.lot_size
        )

        # -----------------------
        # Put DEX
        # -----------------------

        df["PUT_DEX"] = (
            df["PE_DELTA"]
            * df["PE_OI"]
            * spot_price
            * self.lot_size
        )

        # -----------------------
        # Net
        # -----------------------

        df["NET_DEX"] = (
            df["CALL_DEX"]
            +
            df["PUT_DEX"]
        )

        return df

    def total_dex(self, df):

        return df["NET_DEX"].sum()