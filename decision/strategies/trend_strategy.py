from decision.strategies.base_strategy import BaseStrategy


class TrendStrategy(BaseStrategy):
    """
    Trending market adjustment.
    """

    def adjust(self, score, market):

        reasons = []

        # Strong trend deserves a boost
        if market.regime == "TRENDING":

            score += 10

            reasons.append("Trending Market")

        # Strong probability deserves another boost
        if market.probability >= 85:

            score += 5

            reasons.append("Very High Probability")

        return score, reasons