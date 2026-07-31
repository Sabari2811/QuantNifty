import pandas as pd


class DeltaExposureEngine:
    """
    Dealer Delta Exposure

    DEX = Delta × OI × Lot Size

    Adds

        CE_DEX
        PE_DEX
        NET_DEX

    Returns summary statistics.
    """

    def calculate(self, greeks_df: pd.DataFrame):

        df = greeks_df.copy()

        # ---------------------------------------------
        # Lot Size
        # ---------------------------------------------

        if "LOT_SIZE" in df.columns:

            lot = df["LOT_SIZE"]

        else:

            lot = 65

        # ---------------------------------------------
        # CE Exposure
        # ---------------------------------------------

        df["CE_DEX"] = (

            df["CE_DELTA"]

            *

            df["CE_OI"]

            *

            lot

        )

        # ---------------------------------------------
        # PE Exposure
        # ---------------------------------------------

        df["PE_DEX"] = (

            df["PE_DELTA"]

            *

            df["PE_OI"]

            *

            lot

        )

        # ---------------------------------------------
        # Net Exposure
        # ---------------------------------------------

        df["NET_DEX"] = (

            df["CE_DEX"]

            +

            df["PE_DEX"]

        )

        summary = {

            "total_dex": float(df["NET_DEX"].sum()),

            "positive_dex": float(

                df.loc[

                    df["NET_DEX"] > 0,

                    "NET_DEX"

                ].sum()

            ),

            "negative_dex": float(

                df.loc[

                    df["NET_DEX"] < 0,

                    "NET_DEX"

                ].sum()

            )

        }

        return df, summary