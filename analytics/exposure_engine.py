import pandas as pd


class ExposureEngine:

    def calculate(self, greeks_df: pd.DataFrame):

        df = greeks_df.copy()

        # -------------------------------------
        # Call Gamma Exposure
        # -------------------------------------

        df["CE_GEX"] = (
            df["CE_GAMMA"].fillna(0)
            * df["CE_OI"].fillna(0)
        )

        # -------------------------------------
        # Put Gamma Exposure
        # -------------------------------------

        df["PE_GEX"] = (
            df["PE_GAMMA"].fillna(0)
            * df["PE_OI"].fillna(0)
        )

        # -------------------------------------
        # Net Gamma
        # -------------------------------------

        df["NET_GEX"] = (
            df["CE_GEX"]
            - df["PE_GEX"]
        )

        return df