class ProbabilityEngine:
    """
    Institutional Probability Engine

    Combines multiple analytics to produce
    probability scores.

    Current Version:
        Rule-based scoring

    Future:
        Machine Learning model
    """

    def __init__(self):
        pass

    def calculate(
        self,
        dealer,
        iv_skew,
        iv_smile
    ):

        score = 50

        reasons = []

        # -----------------------------------
        # Dealer Gamma
        # -----------------------------------

        if dealer["dealer_gamma"] == "LONG":

            score += 20
            reasons.append("Dealers are Long Gamma")

        else:

            score -= 20
            reasons.append("Dealers are Short Gamma")

        # -----------------------------------
        # Market Mode
        # -----------------------------------

        if dealer["market_mode"] == "PINNED":

            score += 10
            reasons.append("Pinned Market")

        elif dealer["market_mode"] == "TRENDING":

            score -= 10
            reasons.append("Trending Market")

        # -----------------------------------
        # IV Skew
        # -----------------------------------

        if iv_skew["bias"] == "CALLS":

            score += 10
            reasons.append("Call IV Premium")

        elif iv_skew["bias"] == "PUTS":

            score -= 10
            reasons.append("Put IV Premium")

        # -----------------------------------
        # IV Smile
        # -----------------------------------

        if iv_smile["shape"] == "NORMAL":

            score += 5
            reasons.append("Healthy IV Smile")

        else:

            score -= 5
            reasons.append("Abnormal IV Smile")

        score = max(0, min(score, 100))

        return {

            "bullish_probability": score,

            "bearish_probability": 100-score,

            "confidence": abs(score-50)*2,

            "reasons": reasons
        }