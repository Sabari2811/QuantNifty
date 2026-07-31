import pandas as pd


class LiquidityVoidEngine:
    """
    Liquidity Void Detector

    Finds strikes having very low liquidity.

    Criteria
    --------
    Low OI
    Low Volume

    These areas generally allow faster price movement.
    """

    def analyze(
        self,
        greeks_df: pd.DataFrame
    ):

        df = greeks_df.copy()

        # -----------------------------------------
        # Average Values
        # -----------------------------------------

        avg_ce_oi = df["CE_OI"].mean()
        avg_pe_oi = df["PE_OI"].mean()

        avg_ce_vol = df["CE_VOLUME"].mean()
        avg_pe_vol = df["PE_VOLUME"].mean()

        # -----------------------------------------
        # Threshold
        # -----------------------------------------

        oi_threshold = 0.40
        volume_threshold = 0.40

        voids = []

        for _, row in df.iterrows():

            ce_void = (

                row["CE_OI"] < avg_ce_oi * oi_threshold

                and

                row["CE_VOLUME"] < avg_ce_vol * volume_threshold

            )

            pe_void = (

                row["PE_OI"] < avg_pe_oi * oi_threshold

                and

                row["PE_VOLUME"] < avg_pe_vol * volume_threshold

            )

            if ce_void or pe_void:

                voids.append({

                    "strike": float(row["Strike"]),

                    "ce_void": ce_void,

                    "pe_void": pe_void

                })

        return {

            "void_count": len(voids),

            "void_levels": voids

        }