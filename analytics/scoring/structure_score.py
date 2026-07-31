class StructureScore:
    """
    Structure Score

    Maximum Score : 10

    Direction Aware
    """

    MAX_SCORE = 10

    def calculate(

        self,

        market_structure,

        pcr,

        expected_move,

        signal,

        spot

    ):

        score = 0

        reasons = []

        trade = signal.get("signal", "NO TRADE")

        # ==================================================
        # BUY CALL
        # ==================================================

        if trade == "BUY CALL":

            if market_structure["bias"] == "BULLISH":

                score += 4
                reasons.append("Bullish Structure")

            if pcr["oi_pcr"] > 1:

                score += 3
                reasons.append("Bullish PCR")

            if spot < expected_move["upper"]:

                score += 3
                reasons.append("Inside Expected Move")

        # ==================================================
        # BUY PUT
        # ==================================================

        elif trade == "BUY PUT":

            if market_structure["bias"] == "BEARISH":

                score += 4
                reasons.append("Bearish Structure")

            if pcr["oi_pcr"] < 1:

                score += 3
                reasons.append("Bearish PCR")

            if spot > expected_move["lower"]:

                score += 3
                reasons.append("Inside Expected Move")

        # ==================================================
        # Default
        # ==================================================

        else:

            if market_structure["structure"] == "RANGING":

                score += 2

        score = min(score, self.MAX_SCORE)

        return {

            "score": score,

            "max_score": self.MAX_SCORE,

            "reasons": reasons

        }