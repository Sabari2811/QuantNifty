class VolatilityScore:
    """Direction-aware volatility contribution for the NIFTY decision score."""

    MAX_SCORE = 10

    def calculate(self, dealer, iv_skew, iv_smile, atr, signal):
        dealer = dealer or {}
        iv_skew = iv_skew or {}
        atr = atr or {}
        signal = signal or {}
        trade = signal.get("signal", "NO TRADE") if isinstance(signal, dict) else "NO TRADE"
        score = 0
        reasons = []

        expected_volatility = dealer.get("expected_volatility")
        market_sentiment = iv_skew.get("market_sentiment")
        atr_volatility = atr.get("volatility")

        if trade == "BUY CALL":
            if expected_volatility == "LOW":
                score += 3
                reasons.append("Low Expected Volatility")
            elif expected_volatility == "NORMAL":
                score += 2
                reasons.append("Normal Expected Volatility")
            if market_sentiment == "BULLISH":
                score += 4
                reasons.append("Bullish IV Skew")
            if atr_volatility == "NORMAL":
                score += 3
                reasons.append("Normal ATR")
        elif trade == "BUY PUT":
            if expected_volatility == "HIGH":
                score += 3
                reasons.append("High Expected Volatility")
            elif expected_volatility == "NORMAL":
                score += 2
                reasons.append("Normal Expected Volatility")
            if market_sentiment == "BEARISH":
                score += 4
                reasons.append("Bearish IV Skew")
            if atr_volatility == "NORMAL":
                score += 3
                reasons.append("Normal ATR")
        elif atr_volatility == "NORMAL":
            score += 2

        return {
            "score": min(score, self.MAX_SCORE),
            "max_score": self.MAX_SCORE,
            "reasons": reasons,
        }
