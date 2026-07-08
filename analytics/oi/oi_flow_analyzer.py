import numpy as np


class OIFlowAnalyzer:
    """
    Open Interest Flow Analyzer

    Determines whether fresh positions
    are entering the market.

    Returns:

    - Call Writing
    - Put Writing
    - Long Build-up
    - Short Covering
    - Neutral

    Also returns a market bias score.
    """

    def __init__(self):
        pass

    def analyze(self, df):

        result = {}

        ce_oi = df["CE_OI"].sum()
        pe_oi = df["PE_OI"].sum()

        ce_volume = df["CE_VOLUME"].sum()
        pe_volume = df["PE_VOLUME"].sum()

        # -----------------------------
        # PCR
        # -----------------------------

        pcr = pe_oi / ce_oi if ce_oi else 0

        result["pcr"] = round(pcr, 2)

        # -----------------------------
        # Volume Ratio
        # -----------------------------

        volume_ratio = pe_volume / ce_volume if ce_volume else 0

        result["volume_ratio"] = round(volume_ratio, 2)

        # -----------------------------
        # Bias
        # -----------------------------

        if pcr > 1.25:

            result["bias"] = "BULLISH"

        elif pcr < 0.80:

            result["bias"] = "BEARISH"

        else:

            result["bias"] = "NEUTRAL"

        # -----------------------------
        # Flow
        # -----------------------------

        if pcr > 1.3 and volume_ratio > 1:

            flow = "PUT_WRITING"

        elif pcr < 0.75 and volume_ratio < 1:

            flow = "CALL_WRITING"

        elif volume_ratio > 1.2:

            flow = "LONG_BUILDUP"

        elif volume_ratio < 0.8:

            flow = "SHORT_COVERING"

        else:

            flow = "NEUTRAL"

        result["flow"] = flow

        # -----------------------------
        # Scores
        # -----------------------------

        score = 0

        if flow == "PUT_WRITING":
            score += 30

        elif flow == "LONG_BUILDUP":
            score += 20

        elif flow == "CALL_WRITING":
            score -= 30

        elif flow == "SHORT_COVERING":
            score -= 20

        result["score"] = score

        return result