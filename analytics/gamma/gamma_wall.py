import pandas as pd


class GammaWallDetector:
    """
    Detects Gamma Walls from the enriched option chain.
    """

    def detect(self, df):

        if df.empty:
            return None

        idx = df["NET_GEX"].idxmax()

        return df.loc[idx]

    def top_walls(self, df, top_n=5):

        return (
            df.sort_values(
                by="NET_GEX",
                ascending=False
            )
            .head(top_n)
            .reset_index(drop=True)
        )

    def strongest_positive_wall(self, df):

        positive = df[df["NET_GEX"] > 0]

        if positive.empty:
            return None

        return positive.loc[
            positive["NET_GEX"].idxmax()
        ]

    def strongest_negative_wall(self, df):

        negative = df[df["NET_GEX"] < 0]

        if negative.empty:
            return None

        return negative.loc[
            negative["NET_GEX"].idxmin()
        ]

    def summary(self, df):

        primary = self.detect(df)

        positive = self.strongest_positive_wall(df)

        negative = self.strongest_negative_wall(df)

        return {

            "primary_wall": primary,

            "positive_wall": positive,

            "negative_wall": negative,

            "top_walls": self.top_walls(df)

        }