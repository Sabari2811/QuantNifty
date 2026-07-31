from decision.strategies.base_strategy import BaseStrategy


class RangeStrategy(BaseStrategy):
    """
    Range market adjustment.
    """

    def adjust(self, score, market):

        reasons = []

        # Reduce aggressive scores
        score = int(score * 0.70)

        reasons.append("Range Market")

        return score, reasons