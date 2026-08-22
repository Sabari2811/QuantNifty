from decision.strategies.base_strategy import BaseStrategy


class TrendStrategy(BaseStrategy):
    """
    Trending market adjustment.

    Strategy identity:
        TREND

    Strategy adjustments are direction-aware:
    - Positive scores represent BUY CALL direction.
    - Negative scores represent BUY PUT direction.
    - Zero represents WAIT.

    Strategy boosts conviction in the existing direction.
    It must never reverse the direction.
    """

    @property
    def name(self):
        """
        Canonical strategy identity.
        """
        return "TREND"

    def adjust(self, score, market):
        reasons = []

        direction = (
            "BUY CALL"
            if score > 0
            else "BUY PUT"
            if score < 0
            else "WAIT"
        )

        # Strong trend deserves a directional boost
        if market.regime == "TRENDING":
            adjustment = 10

            if direction == "BUY PUT":
                adjustment = -adjustment

            score += adjustment
            reasons.append("Trending Market")

        # Strong probability deserves another directional boost
        if market.probability >= 85:
            adjustment = 5

            if direction == "BUY PUT":
                adjustment = -adjustment

            score += adjustment
            reasons.append("Very High Probability")

        return score, reasons