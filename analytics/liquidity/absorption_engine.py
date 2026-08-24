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

        # Provider failures can leave quote fields as None/NaN.  Do not
        # coerce missing observations to zero: that would manufacture a
        # market observation and could create false absorption signals.
        numeric_columns = [
            "Strike",
            "CE_OI",
            "CE_VOLUME",
            "PE_OI",
            "PE_VOLUME",
        ]

        for column in numeric_columns:
            if column in df.columns:
                df[column] = pd.to_numeric(
                    df[column],
                    errors="coerce",
                )

        ce_valid = df.dropna(
            subset=["Strike", "CE_OI", "CE_VOLUME"]
        )
        pe_valid = df.dropna(
            subset=["Strike", "PE_OI", "PE_VOLUME"]
        )

        absorption = []

        # ------------------------------------------------------
        # CE
        # ------------------------------------------------------
        if not ce_valid.empty:
            avg_ce_oi = ce_valid["CE_OI"].mean()
            avg_ce_vol = ce_valid["CE_VOLUME"].mean()

            for _, row in ce_valid.iterrows():
                if (
                    row["CE_VOLUME"] > avg_ce_vol
                    and row["CE_OI"] < avg_ce_oi
                ):
                    absorption.append({
                        "strike": float(row["Strike"]),
                        "side": "CE",
                        "type": "BUY_ABSORPTION",
                    })

                elif (
                    row["CE_OI"] > avg_ce_oi
                    and row["CE_VOLUME"] < avg_ce_vol
                ):
                    absorption.append({
                        "strike": float(row["Strike"]),
                        "side": "CE",
                        "type": "SELL_ABSORPTION",
                    })

        # ------------------------------------------------------
        # PE
        # ------------------------------------------------------
        if not pe_valid.empty:
            avg_pe_oi = pe_valid["PE_OI"].mean()
            avg_pe_vol = pe_valid["PE_VOLUME"].mean()

            for _, row in pe_valid.iterrows():
                if (
                    row["PE_VOLUME"] > avg_pe_vol
                    and row["PE_OI"] < avg_pe_oi
                ):
                    absorption.append({
                        "strike": float(row["Strike"]),
                        "side": "PE",
                        "type": "BUY_ABSORPTION",
                    })

                elif (
                    row["PE_OI"] > avg_pe_oi
                    and row["PE_VOLUME"] < avg_pe_vol
                ):
                    absorption.append({
                        "strike": float(row["Strike"]),
                        "side": "PE",
                        "type": "SELL_ABSORPTION",
                    })

        return {
            "count": len(absorption),
            "levels": absorption,
        }
