class SignalEngine:
    """
    Institutional Signal Engine

    Generates

    BUY CALL
    BUY PUT
    NO TRADE

    along with

    Confidence
    Reasons
    """

    def __init__(self):

        self.score = 0
        self.reasons = []

    def add_score(self, points, reason):

        self.score += points
        self.reasons.append(reason)

    def reset(self):

        self.score = 0
        self.reasons = []

    def generate(
        self,
        dealer_result
    ):

        self.reset()

        # -------------------------------
        # Dealer Gamma
        # -------------------------------

        if dealer_result["dealer_gamma"] == "SHORT":

            self.add_score(
                25,
                "Dealers Short Gamma"
            )

        else:

            self.add_score(
                10,
                "Dealers Long Gamma"
            )

        # -------------------------------
        # Market Mode
        # -------------------------------

        mode = dealer_result["market_mode"]

        if mode == "TRENDING":

            self.add_score(
                20,
                "Trending Market"
            )

        elif mode == "PINNED":

            self.add_score(
                20,
                "Pinned Market"
            )

        # -------------------------------
        # Breakout Probability
        # -------------------------------

        breakout = dealer_result["breakout_probability"]

        self.score += breakout * 0.20

        self.reasons.append(
            f"Breakout Probability {breakout}%"
        )

        # -------------------------------
        # Mean Reversion
        # -------------------------------

        mr = dealer_result[
            "mean_reversion_probability"
        ]

        self.score += mr * 0.10

        self.reasons.append(
            f"Mean Reversion Probability {mr}%"
        )

        # -------------------------------
        # Final Decision
        # -------------------------------

        if self.score >= 80:

            signal = "BUY_CALL"

            strength = "INSTITUTIONAL"

        elif self.score >= 65:

            signal = "BUY_CALL"

            strength = "STRONG"

        elif self.score >= 50:

            signal = "WATCH"

            strength = "MODERATE"

        else:

            signal = "NO_TRADE"

            strength = "WEAK"

        return {

            "signal": signal,

            "strength": strength,

            "confidence": round(self.score, 2),

            "reasons": self.reasons

        }