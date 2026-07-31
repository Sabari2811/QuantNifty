import pandas as pd


class LiquidityWallEngine:
    """
    Liquidity Wall Engine

    Detects the strongest Call and Put OI walls.

    Output:
        - Call Wall
        - Put Wall
        - Support
        - Resistance
        - Top Call Walls
        - Top Put Walls
    """

    def analyze(self, greeks_df: pd.DataFrame):

        df = greeks_df.copy()

        # -----------------------------------------
        # Top Call Walls
        # -----------------------------------------

        call_df = (
            df[["Strike", "CE_OI"]]
            .sort_values(
                "CE_OI",
                ascending=False
            )
            .head(3)
        )

        # -----------------------------------------
        # Top Put Walls
        # -----------------------------------------

        put_df = (
            df[["Strike", "PE_OI"]]
            .sort_values(
                "PE_OI",
                ascending=False
            )
            .head(3)
        )

        call_wall = float(call_df.iloc[0]["Strike"])

        put_wall = float(put_df.iloc[0]["Strike"])

        return {

            "call_wall": call_wall,

            "put_wall": put_wall,

            "support": put_wall,

            "resistance": call_wall,

            "top_call_walls": call_df.to_dict(
                orient="records"
            ),

            "top_put_walls": put_df.to_dict(
                orient="records"
            )

        }