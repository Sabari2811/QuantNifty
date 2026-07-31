import pandas as pd


class GammaWallDetector:
    """
    Detects Gamma Wall levels.

    Gamma Wall:
        Strike having the highest NET_GEX.

    Positive Wall:
        Strike with highest positive NET_GEX.

    Negative Wall:
        Strike with lowest (most negative) NET_GEX.
    """

    # ======================================================
    # MAIN
    # ======================================================

    def analyze(self, df):

        if df is None or df.empty:
            return {
                "gamma_wall": None,
                "call_wall": None,
                "put_wall": None,
                "net_gex": None
            }

        if "NET_GEX" not in df.columns:
            return {
                "gamma_wall": None,
                "call_wall": None,
                "put_wall": None,
                "net_gex": None
            }

        # ----------------------------
        # Gamma Wall
        # ----------------------------

        idx = df["NET_GEX"].idxmax()

        row = df.loc[idx]

        gamma_wall = row["Strike"]
        net_gex = row["NET_GEX"]

        # ----------------------------
        # Call Wall
        # Highest Positive GEX
        # ----------------------------

        positive = df[df["NET_GEX"] > 0]

        if positive.empty:
            call_wall = None
        else:
            call_wall = positive.loc[
                positive["NET_GEX"].idxmax(),
                "Strike"
            ]

        # ----------------------------
        # Put Wall
        # Most Negative GEX
        # ----------------------------

        negative = df[df["NET_GEX"] < 0]

        if negative.empty:
            put_wall = None
        else:
            put_wall = negative.loc[
                negative["NET_GEX"].idxmin(),
                "Strike"
            ]

        return {

            "gamma_wall": gamma_wall,

            "call_wall": call_wall,

            "put_wall": put_wall,

            "net_gex": float(net_gex)

        }

    # ======================================================
    # Helpers
    # ======================================================

    def top_walls(self, df, top_n=5):

        if df is None or df.empty:
            return pd.DataFrame()

        return (

            df.sort_values(

                by="NET_GEX",

                ascending=False

            )

            .head(top_n)

            .reset_index(drop=True)

        )

    def summary(self, df):

        return self.analyze(df)

    # ======================================================
    # Backward Compatibility
    # ======================================================

    def detect(self, df):

        return self.analyze(df)