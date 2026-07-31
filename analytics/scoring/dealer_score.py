class DealerScore:
    """
    Dealer Score

    Maximum Score : 20

    Direction Aware
    """

    MAX_SCORE = 20

    def calculate(

        self,

        dealer,

        dealer_flow,

        signal

    ):

        score = 0

        reasons = []

        trade = signal.get("signal", "NO TRADE")

        # ====================================================
        # BUY CALL
        # ====================================================

        if trade == "BUY CALL":

            if dealer["dealer_gamma"] == "LONG":
                score += 6
                reasons.append("Dealers Long Gamma")

            if dealer["market_mode"] == "TRENDING":
                score += 4
                reasons.append("Trending Market")

            if dealer_flow["dealer_delta"] == "LONG":
                score += 5
                reasons.append("Positive Delta")

            if dealer_flow["dealer_vanna"] == "POSITIVE":
                score += 5
                reasons.append("Positive Vanna")

        # ====================================================
        # BUY PUT
        # ====================================================

        elif trade == "BUY PUT":

            if dealer["dealer_gamma"] == "SHORT":
                score += 6
                reasons.append("Dealers Short Gamma")

            if dealer["market_mode"] == "TRENDING":
                score += 4
                reasons.append("Trending Market")

            if dealer_flow["dealer_delta"] == "LONG":
                score += 5
                reasons.append("Dealers Hedging")

            if dealer_flow["dealer_charm"] == "NEGATIVE":
                score += 5
                reasons.append("Negative Charm")

        # ====================================================
        # NO TRADE
        # ====================================================

        else:

            if dealer["dealer_gamma"] == "LONG":
                score += 3

            if dealer["market_mode"] == "TRENDING":
                score += 2

        score = min(score, self.MAX_SCORE)

        return {

            "score": score,

            "max_score": self.MAX_SCORE,

            "reasons": reasons

        }