import pandas as pd


class AbsorptionEngine:
    """
    Institutional Absorption Detector

    Detects possible institutional absorption using
    OI and Volume.

    BUY Absorption
        High Volume
        Low OI

    SELL Absorption
        High OI
        Low Volume
    """

    def analyze(self, greeks_df: pd.DataFrame):

        df = greeks_df.copy()

        avg_ce_oi = df["CE_OI"].mean()
        avg_pe_oi = df["PE_OI"].mean()

        avg_ce_vol = df["CE_VOLUME"].mean()
        avg_pe_vol = df["PE_VOLUME"].mean()

        absorption = []

        for _, row in df.iterrows():

            # -----------------------------
            # CE
            # -----------------------------

            if (
                row["CE_VOLUME"] > avg_ce_vol
                and
                row["CE_OI"] < avg_ce_oi
            ):

                absorption.append({

                    "strike": float(row["Strike"]),

                    "side": "CE",

                    "type": "BUY_ABSORPTION"

                })

            elif (
                row["CE_OI"] > avg_ce_oi
                and
                row["CE_VOLUME"] < avg_ce_vol
            ):

                absorption.append({

                    "strike": float(row["Strike"]),

                    "side": "CE",

                    "type": "SELL_ABSORPTION"

                })

            # -----------------------------
            # PE
            # -----------------------------

            if (
                row["PE_VOLUME"] > avg_pe_vol
                and
                row["PE_OI"] < avg_pe_oi
            ):

                absorption.append({

                    "strike": float(row["Strike"]),

                    "side": "PE",

                    "type": "BUY_ABSORPTION"

                })

            elif (
                row["PE_OI"] > avg_pe_oi
                and
                row["PE_VOLUME"] < avg_pe_vol
            ):

                absorption.append({

                    "strike": float(row["Strike"]),

                    "side": "PE",

                    "type": "SELL_ABSORPTION"

                })

        return {

            "count": len(absorption),

            "levels": absorption

        }