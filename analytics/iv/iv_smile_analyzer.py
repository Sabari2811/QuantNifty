import pandas as pd


class IVSmileAnalyzer:
    """
    IV Smile Analyzer

    Measures IV distribution across strikes.

    Handles missing IV gracefully.
    """

    def analyze(self, df: pd.DataFrame):

        if df is None or df.empty:

            return self._unknown()

        df = df.copy()

        # ---------------------------------------
        # Ensure columns exist
        # ---------------------------------------

        for col in ["CE_IV", "PE_IV"]:

            if col not in df.columns:
                df[col] = pd.NA

            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

        # ---------------------------------------
        # No IV available
        # ---------------------------------------

        if df["CE_IV"].dropna().empty and df["PE_IV"].dropna().empty:
            return self._unknown()

        result = {}

        # ---------------------------------------
        # CALL IV
        # ---------------------------------------

        if df["CE_IV"].dropna().empty:

            result["ce_peak_iv"] = 0
            result["ce_peak_strike"] = None
            result["ce_avg_iv"] = 0
            result["ce_min_iv"] = 0
            result["ce_smile_width"] = 0

        else:

            result["ce_peak_iv"] = float(df["CE_IV"].max())

            result["ce_peak_strike"] = df.loc[
                df["CE_IV"].idxmax(),
                "Strike"
            ]

            result["ce_avg_iv"] = float(df["CE_IV"].mean())

            result["ce_min_iv"] = float(df["CE_IV"].min())

            result["ce_smile_width"] = (
                result["ce_peak_iv"]
                -
                result["ce_min_iv"]
            )

        # ---------------------------------------
        # PUT IV
        # ---------------------------------------

        if df["PE_IV"].dropna().empty:

            result["pe_peak_iv"] = 0
            result["pe_peak_strike"] = None
            result["pe_avg_iv"] = 0
            result["pe_min_iv"] = 0
            result["pe_smile_width"] = 0

        else:

            result["pe_peak_iv"] = float(df["PE_IV"].max())

            result["pe_peak_strike"] = df.loc[
                df["PE_IV"].idxmax(),
                "Strike"
            ]

            result["pe_avg_iv"] = float(df["PE_IV"].mean())

            result["pe_min_iv"] = float(df["PE_IV"].min())

            result["pe_smile_width"] = (
                result["pe_peak_iv"]
                -
                result["pe_min_iv"]
            )

        # ---------------------------------------
        # Dominant Side
        # ---------------------------------------

        if result["ce_smile_width"] > result["pe_smile_width"]:

            result["dominant_side"] = "CALL"

        elif result["pe_smile_width"] > result["ce_smile_width"]:

            result["dominant_side"] = "PUT"

        else:

            result["dominant_side"] = "BALANCED"

        return result

    def _unknown(self):

        return {

            "ce_peak_iv": 0,
            "pe_peak_iv": 0,

            "ce_peak_strike": None,
            "pe_peak_strike": None,

            "ce_avg_iv": 0,
            "pe_avg_iv": 0,

            "ce_min_iv": 0,
            "pe_min_iv": 0,

            "ce_smile_width": 0,
            "pe_smile_width": 0,

            "dominant_side": "UNKNOWN"

        }