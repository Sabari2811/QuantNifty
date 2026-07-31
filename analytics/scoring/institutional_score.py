class InstitutionalScore:
    """
    Combines all scoring engines.

    Maximum Score : 100
    """

    MAX_SCORE = 100

    def calculate(

        self,

        dealer_score,

        liquidity_score,

        gamma_score,

        structure_score,

        volatility_score

    ):

        total = (

            dealer_score["score"]

            + liquidity_score["score"]

            + gamma_score["score"]

            + structure_score["score"]

            + volatility_score["score"]

        )

        # ==========================================
        # Grade
        # ==========================================

        if total >= 90:

            grade = "A+"
            strength = "VERY STRONG"
            signal = "BUY CALL"

        elif total >= 80:

            grade = "A"
            strength = "STRONG"
            signal = "BUY CALL"

        elif total >= 70:

            grade = "B+"
            strength = "GOOD"
            signal = "BUY"

        elif total >= 60:

            grade = "B"
            strength = "MODERATE"
            signal = "WATCH"

        elif total >= 50:

            grade = "C"
            strength = "WEAK"
            signal = "WAIT"

        else:

            grade = "D"
            strength = "AVOID"
            signal = "NO TRADE"

        confidence = min(100, total)

        reasons = (

            dealer_score["reasons"]

            + liquidity_score["reasons"]

            + gamma_score["reasons"]

            + structure_score["reasons"]

            + volatility_score["reasons"]

        )

        return {

            "score": total,

            "max_score": self.MAX_SCORE,

            "grade": grade,

            "strength": strength,

            "signal": signal,

            "confidence": confidence,

            "reasons": reasons

        }