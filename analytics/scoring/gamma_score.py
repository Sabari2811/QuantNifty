class GammaScore:
    """
    Gamma Score

    Maximum Score : 15

    Direction Aware
    """

    MAX_SCORE = 15

    def calculate(

        self,

        dealer,

        signal

    ):

        score = 0

        reasons = []

        trade = signal.get("signal", "NO TRADE")

        # ======================================
        # BUY CALL
        # ======================================

        if trade == "BUY CALL":

            if dealer["dealer_gamma"] == "LONG":

                score += 8
                reasons.append("Dealers Long Gamma")

            if dealer["gamma_flip"] is not None:

                score += 4
                reasons.append("Gamma Flip")

            if dealer["total_gex"] > 0:

                score += 3
                reasons.append("Positive GEX")

        # ======================================
        # BUY PUT
        # ======================================

        elif trade == "BUY PUT":

            if dealer["dealer_gamma"] == "SHORT":

                score += 8
                reasons.append("Dealers Short Gamma")

            if dealer["gamma_flip"] is not None:

                score += 4
                reasons.append("Gamma Flip")

            if dealer["total_gex"] < 0:

                score += 3
                reasons.append("Negative GEX")

        # ======================================
        # Default
        # ======================================

        else:

            if dealer["gamma_flip"] is not None:

                score += 3

        score = min(score, self.MAX_SCORE)

        return {

            "score": score,

            "max_score": self.MAX_SCORE,

            "reasons": reasons

        }