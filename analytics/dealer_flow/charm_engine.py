import pandas as pd


class CharmEngine:
    """
    Dealer Charm Exposure

    Approximation:

        CHARM = Theta / Spot

    Exposure:

        CHARM × OI × Lot Size
    """

    def calculate(
        self,
        greeks_df: pd.DataFrame,
        spot: float
    ):

        df = greeks_df.copy()

        if "LOT_SIZE" in df.columns:
            lot = df["LOT_SIZE"]
        else:
            lot = 65

        # ---------------------------------------
        # CE
        # ---------------------------------------

        df["CE_CHARM"] = (

            df["CE_THETA"]

            / spot

            * df["CE_OI"]

            * lot

        )

        # ---------------------------------------
        # PE
        # ---------------------------------------

        df["PE_CHARM"] = (

            df["PE_THETA"]

            / spot

            * df["PE_OI"]

            * lot

        )

        # ---------------------------------------
        # Net
        # ---------------------------------------

        df["NET_CHARM"] = (

            df["CE_CHARM"]

            +

            df["PE_CHARM"]

        )

        summary = {

            "total_charm": float(
                df["NET_CHARM"].sum()
            ),

            "positive_charm": float(
                df.loc[
                    df["NET_CHARM"] > 0,
                    "NET_CHARM"
                ].sum()
            ),

            "negative_charm": float(
                df.loc[
                    df["NET_CHARM"] < 0,
                    "NET_CHARM"
                ].sum()
            )

        }

        return df, summary