import pandas as pd


class GammaFlipDetector:

    # ======================================================
    # Standard API
    # ======================================================

    def analyze(self, df: pd.DataFrame):

        if "NET_GEX" not in df.columns:
            raise ValueError("NET_GEX column not found.")

        previous_gamma = None
        previous_row = None

        for _, row in df.iterrows():

            current_gamma = row["NET_GEX"]

            if previous_gamma is None:

                previous_gamma = current_gamma
                previous_row = row
                continue

            if previous_gamma < 0 <= current_gamma:

                return {

                    "flip_found": True,

                    "direction": "NEGATIVE_TO_POSITIVE",

                    "lower_strike": previous_row["Strike"],

                    "upper_strike": row["Strike"],

                    "gamma_flip": row["Strike"]

                }

            if previous_gamma > 0 >= current_gamma:

                return {

                    "flip_found": True,

                    "direction": "POSITIVE_TO_NEGATIVE",

                    "lower_strike": previous_row["Strike"],

                    "upper_strike": row["Strike"],

                    "gamma_flip": row["Strike"]

                }

            previous_gamma = current_gamma
            previous_row = row

        return {

            "flip_found": False,

            "direction": None,

            "lower_strike": None,

            "upper_strike": None,

            "gamma_flip": None

        }

    # ======================================================
    # Backward Compatibility
    # ======================================================

    def detect(self, df):

        return self.analyze(df)

    def find_flip(self, df):

        return self.analyze(df)