import pandas as pd


class VannaEngine:
    """
    Dealer Vanna Exposure

    Approximation:

        VANNA = VEGA / SPOT

    Exposure:

        VANNA × OI × LOT_SIZE
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

        # ---------------------------------
        # CE
        # ---------------------------------

        df["CE_VANNA"] = (

            df["CE_VEGA"]

            / spot

            * df["CE_OI"]

            * lot

        )

        # ---------------------------------
        # PE
        # ---------------------------------

        df["PE_VANNA"] = (

            df["PE_VEGA"]

            / spot

            * df["PE_OI"]

            * lot

        )

        # ---------------------------------
        # Net
        # ---------------------------------

        df["NET_VANNA"] = (

            df["CE_VANNA"]

            +

            df["PE_VANNA"]

        )

        summary = {

            "total_vanna": float(df["NET_VANNA"].sum()),

            "positive_vanna": float(
                df.loc[
                    df["NET_VANNA"] > 0,
                    "NET_VANNA"
                ].sum()
            ),

            "negative_vanna": float(
                df.loc[
                    df["NET_VANNA"] < 0,
                    "NET_VANNA"
                ].sum()
            )

        }

        return df, summary