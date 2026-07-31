import pandas as pd


class IVSkewAnalyzer:
    """
    Institutional IV Skew Analyzer

    Safe against missing option quotes.
    """

    def analyze(self, df: pd.DataFrame):

        if df is None or df.empty:

            return self._unknown()

        df = df.copy()

        for col in ["CE_IV", "PE_IV"]:

            if col not in df.columns:
                df[col] = pd.NA

            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

        call_iv = df["CE_IV"].mean(skipna=True)
        put_iv = df["PE_IV"].mean(skipna=True)

        if pd.isna(call_iv):
            call_iv = 0

        if pd.isna(put_iv):
            put_iv = 0

        skew = call_iv - put_iv

        # ---------------------------------------
        # Bias
        # ---------------------------------------

        if skew > 0.02:

            bias = "CALLS_EXPENSIVE"
            sentiment = "BULLISH"

        elif skew < -0.02:

            bias = "PUTS_EXPENSIVE"
            sentiment = "BEARISH"

        else:

            bias = "BALANCED"
            sentiment = "NEUTRAL"

        # ---------------------------------------
        # Volatility
        # ---------------------------------------

        highest_iv = max(call_iv, put_iv)

        if highest_iv > 0.30:

            volatility = "VERY_HIGH"

        elif highest_iv > 0.20:

            volatility = "HIGH"

        elif highest_iv > 0.10:

            volatility = "NORMAL"

        else:

            volatility = "LOW"

        return {

            "average_call_iv": round(call_iv, 4),

            "average_put_iv": round(put_iv, 4),

            "iv_skew": round(skew, 4),

            "iv_bias": bias,

            "market_sentiment": sentiment,

            "volatility": volatility

        }

    def _unknown(self):

        return {

            "average_call_iv": 0,

            "average_put_iv": 0,

            "iv_skew": 0,

            "iv_bias": "UNKNOWN",

            "market_sentiment": "UNKNOWN",

            "volatility": "UNKNOWN"

        }