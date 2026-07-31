class VolatilityScore:
    """
    Volatility Score

    Maximum Score : 10

    Direction Aware
    """

    MAX_SCORE = 10

    def calculate(

        self,

        dealer,

        iv_skew,

        iv_smile,

        atr,

        signal

    ):

        score = 0

        reasons = []

        trade = signal.get("signal", "NO TRADE")

        # ==========================================
        # BUY CALL
        # ==========================================

        if trade == "BUY CALL":

            if dealer["expected_volatility"] == "LOW":

                score += 3
                reasons.append("Low Expected Volatility")

            elif dealer["expected_volatility"] == "NORMAL":

                score += 2
                reasons.append("Normal Expected Volatility")

            if iv_skew["market_sentiment"] == "BULLISH":

                score += 4
                reasons.append("Bullish IV Skew")

            if atr["volatility"] == "NORMAL":

                score += 3
                reasons.append("Normal ATR")

        # ==========================================
        # BUY PUT
        # ==========================================

        elif trade == "BUY PUT":

            if dealer["expected_volatility"] == "HIGH":

                score += 3
                reasons.append("High Expected Volatility")

            elif dealer["expected_volatility"] == "NORMAL":

                score += 2
                reasons.append("Normal Expected Volatility")

            if iv_skew["market_sentiment"] == "BEARISH":

                score += 4
                reasons.append("Bearish IV Skew")

            if atr["volatility"] == "NORMAL":

                score += 3
                reasons.append("Normal ATR")

        # ==========================================
        # Default
        # ==========================================

        else:

            if atr["volatility"] == "NORMAL":

                score += 2

        score = min(score, self.MAX_SCORE)

        return {

            "score": score,

            "max_score": self.MAX_SCORE,

            "reasons": reasons

        }