class ProbabilityEngine:
    """
    Institutional Probability Engine

    Combines

    - Dealer Position
    - Market Structure
    - PCR
    - IV Skew
    - Technical Analysis

    Produces

        Bullish Probability
        Bearish Probability
        Confidence
    """

    def __init__(self):
        pass

    def calculate(

        self,

        dealer,

        market_structure,

        pcr,

        iv_skew,

        technical

    ):

        bullish = 50
        bearish = 50

        reasons = []

        # ==================================================
        # Dealer Gamma
        # ==================================================

        if dealer.get("dealer_gamma") == "LONG":

            bullish += 20
            bearish -= 20

            reasons.append("Dealers Long Gamma")

        elif dealer.get("dealer_gamma") == "SHORT":

            bullish -= 20
            bearish += 20

            reasons.append("Dealers Short Gamma")

        # ==================================================
        # Market Mode
        # ==================================================

        mode = dealer.get("market_mode", "UNKNOWN")

        if mode == "PINNED":

            bullish += 5
            bearish -= 5

            reasons.append("Pinned Market")

        elif mode == "TRENDING":

            bullish -= 5
            bearish += 5

            reasons.append("Trending Market")

        # ==================================================
        # PCR
        # ==================================================

        sentiment = pcr.get("sentiment", "NEUTRAL")

        if sentiment == "BULLISH":

            bullish += 10
            bearish -= 10

            reasons.append("Bullish PCR")

        elif sentiment == "BEARISH":

            bullish -= 10
            bearish += 10

            reasons.append("Bearish PCR")

        # ==================================================
        # IV Skew
        # ==================================================

        bias = iv_skew.get("iv_bias", "UNKNOWN")

        if bias == "CALLS_EXPENSIVE":

            bullish += 5
            bearish -= 5

            reasons.append("Call IV Expensive")

        elif bias == "PUTS_EXPENSIVE":

            bullish -= 5
            bearish += 5

            reasons.append("Put IV Expensive")

        # ==================================================
        # Technical Analysis
        # ==================================================

        ema = technical.get("ema", {})
        rsi = technical.get("rsi", {})
        vwap = technical.get("vwap", {})
        adx = technical.get("adx", {})

        # EMA Trend

        trend = ema.get("trend", "UNKNOWN")

        if trend in ("BULLISH", "STRONG_BULLISH"):

            bullish += 10
            bearish -= 10

            reasons.append("EMA Bullish")

        elif trend in ("BEARISH", "STRONG_BEARISH"):

            bullish -= 10
            bearish += 10

            reasons.append("EMA Bearish")

        # RSI

        state = rsi.get("state", "UNKNOWN")

        if state == "BULLISH":

            bullish += 5
            bearish -= 5

            reasons.append("RSI Bullish")

        elif state == "BEARISH":

            bullish -= 5
            bearish += 5

            reasons.append("RSI Bearish")

        elif state == "OVERBOUGHT":

            bearish += 5

            reasons.append("RSI Overbought")

        elif state == "OVERSOLD":

            bullish += 5

            reasons.append("RSI Oversold")

        # VWAP

        position = vwap.get("position", "UNKNOWN")

        if position == "ABOVE":

            bullish += 5
            bearish -= 5

            reasons.append("Above VWAP")

        elif position == "BELOW":

            bullish -= 5
            bearish += 5

            reasons.append("Below VWAP")

        # ADX

        strength = adx.get("strength", "UNKNOWN")

        if strength in ("STRONG", "VERY_STRONG"):

            bullish += 5

            reasons.append("Strong Trend")

        # ==================================================
        # Clamp
        # ==================================================

        bullish = max(0, min(100, bullish))
        bearish = max(0, min(100, bearish))

        confidence = abs(bullish - bearish)

        # ==================================================
        # Result
        # ==================================================

        return {

            "bullish_probability": bullish,

            "bearish_probability": bearish,

            "confidence": confidence,

            "reasons": reasons

        }