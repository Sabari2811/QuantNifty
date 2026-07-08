import pandas as pd


class VannaExposureEngine:

    """
    Vanna Exposure Engine

    Calculates:

        Vanna Exposure (VEX)

    Formula

        VEX = Vanna × OI × Lot Size

    """

    def __init__(self, lot_size=75):

        self.lot_size = lot_size

    def calculate(self, df: pd.DataFrame):

        data = df.copy()

        # ------------------------
        # Estimate Vanna
        #
        # Approximation
        #
        # Vanna ≈ Gamma × Vega
        # ------------------------

        data["CE_VANNA"] = (
            data["CE_GAMMA"]
            * data["CE_VEGA"]
        )

        data["PE_VANNA"] = (
            data["PE_GAMMA"]
            * data["PE_VEGA"]
        )

        # ------------------------

        data["CE_VEX"] = (
            data["CE_VANNA"]
            * data["CE_OI"]
            * self.lot_size
        )

        data["PE_VEX"] = (
            data["PE_VANNA"]
            * data["PE_OI"]
            * self.lot_size
        )

        data["NET_VEX"] = (

            data["CE_VEX"]

            -

            data["PE_VEX"]

        )

        return data

    def total_vex(self, df):

        return df["NET_VEX"].sum()