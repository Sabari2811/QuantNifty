class TradeQualityEngine:
    """
    Scores the overall quality of a trade.

    Score Range:
        0 - 100
    """

    def score(self, decision):

        trade = decision.trade

        contract = trade.contract

        if contract is None:

            return 0

        score = 0

        # --------------------------------------
        # Risk Reward
        # --------------------------------------

        rr = trade.risk_reward

        if rr >= 2:

            score += 30

        elif rr >= 1.5:

            score += 20

        elif rr >= 1:

            score += 10

        # --------------------------------------
        # IV
        # --------------------------------------

        iv = contract.iv

        if 10 <= iv <= 25:

            score += 20

        elif 5 <= iv < 10:

            score += 10

        # --------------------------------------
        # Open Interest
        # --------------------------------------

        if contract.oi >= 100000:

            score += 20

        elif contract.oi >= 50000:

            score += 10

        # --------------------------------------
        # Volume
        # --------------------------------------

        if contract.volume >= 50000:

            score += 20

        elif contract.volume >= 20000:

            score += 10

        # --------------------------------------
        # Delta
        # --------------------------------------

        if 0.30 <= abs(contract.delta) <= 0.70:

            score += 10

        return min(score, 100)