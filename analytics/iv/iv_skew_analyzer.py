import pandas as pd


class IVSkewAnalyzer:

    """
    Institutional IV Analyzer

    Calculates

    • Average Call IV
    • Average Put IV
    • IV Skew
    • Market Bias
    • Volatility Regime
    """

    def analyze(self, df: pd.DataFrame):

        if df.empty:

            return {
                "average_call_iv": 0,
                "average_put_iv": 0,
                "iv_skew": 0,
                "iv_bias": "UNKNOWN",
                "market_sentiment": "UNKNOWN",
                "volatility": "UNKNOWN"
            }

        call_iv = df["CE_IV"].mean()

        put_iv = df["PE_IV"].mean()

        skew = call_iv - put_iv

        # ------------------------------------
        # Skew Bias
        # ------------------------------------

        if skew > 0.02:

            bias = "CALLS_EXPENSIVE"

            sentiment = "BULLISH"

        elif skew < -0.02:

            bias = "PUTS_EXPENSIVE"

            sentiment = "BEARISH"

        else:

            bias = "BALANCED"

            sentiment = "NEUTRAL"

        # ------------------------------------
        # Volatility Regime
        # ------------------------------------

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