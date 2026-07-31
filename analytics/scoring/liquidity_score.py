class LiquidityScore:
    """
    Liquidity Score

    Maximum Score : 15

    Direction Aware
    """

    MAX_SCORE = 15

    def calculate(

        self,

        liquidity,

        signal,

        spot

    ):

        score = 0

        reasons = []

        trade = signal.get("signal", "NO TRADE")

        support = liquidity["support"]

        resistance = liquidity["resistance"]

        absorption = liquidity["absorption"]

        # =====================================================
        # BUY CALL
        # =====================================================

        if trade == "BUY CALL":

            if support is not None and spot > support:

                score += 5
                reasons.append("Above Support")

            if absorption["count"] > 0:

                score += 5
                reasons.append("Institutional Absorption")

            if liquidity["order_imbalance"]["buy_pressure"]:

                score += 5
                reasons.append("Buy Pressure")

        # =====================================================
        # BUY PUT
        # =====================================================

        elif trade == "BUY PUT":

            if resistance is not None and spot < resistance:

                score += 5
                reasons.append("Below Resistance")

            if absorption["count"] > 0:

                score += 5
                reasons.append("Institutional Absorption")

            if liquidity["order_imbalance"]["sell_pressure"]:

                score += 5
                reasons.append("Sell Pressure")

        # =====================================================
        # Default
        # =====================================================

        else:

            if absorption["count"] > 0:

                score += 3

        score = min(score, self.MAX_SCORE)

        return {

            "score": score,

            "max_score": self.MAX_SCORE,

            "reasons": reasons

        }