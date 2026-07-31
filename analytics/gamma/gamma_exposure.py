import pandas as pd


class GammaExposureEngine:
    """
    Gamma Exposure (GEX)

    Computes

        CE_GEX
        PE_GEX
        NET_GEX

    Formula

        GEX = Gamma × OI × Lot Size

    NET_GEX = CE_GEX - PE_GEX
    """

    def __init__(self, lot_size=65):

        self.lot_size = lot_size

    # ======================================================
    # Standard API
    # ======================================================

    def analyze(self, df: pd.DataFrame):

        df = df.copy()

        required = [

            "CE_GAMMA",
            "PE_GAMMA",
            "CE_OI",
            "PE_OI"

        ]

        for col in required:

            if col not in df.columns:

                df[col] = 0

            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            ).fillna(0)

        df["CE_GEX"] = (

            df["CE_GAMMA"]
            *
            df["CE_OI"]
            *
            self.lot_size

        )

        df["PE_GEX"] = (

            df["PE_GAMMA"]
            *
            df["PE_OI"]
            *
            self.lot_size

        )

        df["NET_GEX"] = (

            df["CE_GEX"]
            -
            df["PE_GEX"]

        )

        return df

    # ======================================================
    # Backward Compatibility
    # ======================================================

    def calculate(self, df):

        return self.analyze(df)