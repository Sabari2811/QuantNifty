class ProbabilityEngine:
    """Build directional probabilities for the NIFTY decision engine.

    Trend strength increases conviction only; it never creates a bullish
    direction by itself. Direction must come from directional inputs.
    """

    def calculate(self, dealer, market_structure, pcr, iv_skew, technical):
        bullish = 50
        bearish = 50
        reasons = []
        bullish_confirmations = 0
        bearish_confirmations = 0

        if dealer.get("dealer_gamma") == "LONG":
            bullish += 20
            bearish -= 20
            bullish_confirmations += 1
            reasons.append("Dealers Long Gamma")
        elif dealer.get("dealer_gamma") == "SHORT":
            bullish -= 20
            bearish += 20
            bearish_confirmations += 1
            reasons.append("Dealers Short Gamma")

        mode = dealer.get("market_mode", "UNKNOWN")
        if mode == "PINNED":
            reasons.append("Pinned Market")
        elif mode == "TRENDING":
            reasons.append("Trending Market")

        sentiment = pcr.get("sentiment", "NEUTRAL")
        if sentiment == "BULLISH":
            bullish += 10
            bearish -= 10
            bullish_confirmations += 1
            reasons.append("Bullish PCR")
        elif sentiment == "BEARISH":
            bullish -= 10
            bearish += 10
            bearish_confirmations += 1
            reasons.append("Bearish PCR")

        bias = iv_skew.get("iv_bias", "UNKNOWN")
        if bias == "CALLS_EXPENSIVE":
            bullish += 5
            bearish -= 5
            reasons.append("Call IV Expensive")
        elif bias == "PUTS_EXPENSIVE":
            bullish -= 5
            bearish += 5
            reasons.append("Put IV Expensive")

        ema = technical.get("ema", {})
        rsi = technical.get("rsi", {})
        vwap = technical.get("vwap", {})
        adx = technical.get("adx", {})

        trend = ema.get("trend", "UNKNOWN")
        if trend in ("BULLISH", "STRONG_BULLISH"):
            bullish += 10
            bearish -= 10
            bullish_confirmations += 1
            reasons.append("EMA Bullish")
        elif trend in ("BEARISH", "STRONG_BEARISH"):
            bullish -= 10
            bearish += 10
            bearish_confirmations += 1
            reasons.append("EMA Bearish")

        state = rsi.get("state", "UNKNOWN")
        if state == "BULLISH":
            bullish += 5
            bearish -= 5
            bullish_confirmations += 1
            reasons.append("RSI Bullish")
        elif state == "BEARISH":
            bullish -= 5
            bearish += 5
            bearish_confirmations += 1
            reasons.append("RSI Bearish")
        elif state == "OVERBOUGHT":
            bearish += 5
            reasons.append("RSI Overbought")
        elif state == "OVERSOLD":
            bullish += 5
            reasons.append("RSI Oversold")

        position = vwap.get("position", "UNKNOWN")
        if position == "ABOVE":
            bullish += 5
            bearish -= 5
            bullish_confirmations += 1
            reasons.append("Above VWAP")
        elif position == "BELOW":
            bullish -= 5
            bearish += 5
            bearish_confirmations += 1
            reasons.append("Below VWAP")

        # ADX is explicitly direction-neutral: it strengthens the dominant
        # side rather than introducing an arbitrary bullish bias.
        if adx.get("strength", "UNKNOWN") in ("STRONG", "VERY_STRONG"):
            if bullish > bearish:
                bullish += 5
            elif bearish > bullish:
                bearish += 5
            reasons.append("Strong Trend")

        bullish = max(0, min(100, bullish))
        bearish = max(0, min(100, bearish))
        confidence = abs(bullish - bearish)

        return {
            "bullish_probability": bullish,
            "bearish_probability": bearish,
            "confidence": confidence,
            "bullish_confirmations": bullish_confirmations,
            "bearish_confirmations": bearish_confirmations,
            "reasons": reasons,
        }
