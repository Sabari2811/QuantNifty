import pandas as pd


class IVSmileAnalyzer:

    """
    Analyses IV distribution across strikes.
    """

    def analyze(self, df: pd.DataFrame):

        result = {}

        result["ce_peak_iv"] = df["CE_IV"].max()
        result["pe_peak_iv"] = df["PE_IV"].max()

        result["ce_peak_strike"] = (
            df.loc[df["CE_IV"].idxmax(), "Strike"]
        )

        result["pe_peak_strike"] = (
            df.loc[df["PE_IV"].idxmax(), "Strike"]
        )

        result["ce_avg_iv"] = df["CE_IV"].mean()
        result["pe_avg_iv"] = df["PE_IV"].mean()

        result["ce_min_iv"] = df["CE_IV"].min()
        result["pe_min_iv"] = df["PE_IV"].min()

        result["ce_smile_width"] = (
            result["ce_peak_iv"] -
            result["ce_min_iv"]
        )

        result["pe_smile_width"] = (
            result["pe_peak_iv"] -
            result["pe_min_iv"]
        )

        if result["ce_smile_width"] > result["pe_smile_width"]:
            result["dominant_side"] = "CALL"
        elif result["pe_smile_width"] > result["ce_smile_width"]:
            result["dominant_side"] = "PUT"
        else:
            result["dominant_side"] = "BALANCED"

        return result