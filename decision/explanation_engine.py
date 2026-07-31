from decision.explanation import Explanation
from decision.constants import Signal


class ExplanationEngine:
    """
    Converts technical analytics into
    human-readable market intelligence.

    No calculations are performed here.

    It only explains the output produced by the
    Decision Engine.
    """

    def build(
        self,
        decision,
        regime,
        snapshot
    ):

        explanation = Explanation()

        # =====================================================
        # Confidence
        # =====================================================

        explanation.confidence = decision.signal.confidence

        # =====================================================
        # Recommendation
        # =====================================================

        if decision.signal.name == Signal.BUY_CALL.value:

            explanation.title = "Bullish Opportunity"

            explanation.recommendation = (
                "BUY CALL"
            )

        elif decision.signal.name == Signal.BUY_PUT.value:

            explanation.title = "Bearish Opportunity"

            explanation.recommendation = (
                "BUY PUT"
            )

        else:

            explanation.title = "No Trade"

            explanation.recommendation = (
                "WAIT"
            )

        # =====================================================
        # Strengths
        # =====================================================

        for reason in decision.reasons:

            if any(word in reason for word in (
                "LONG",
                "Positive",
                "Bullish",
                "High",
                "Buying",
                "STRONG"
            )):

                explanation.strengths.append(reason)

        # =====================================================
        # Weaknesses
        # =====================================================

        for reason in decision.reasons:

            if any(word in reason for word in (
                "SHORT",
                "Negative",
                "Weak",
                "Low",
                "BEARISH"
            )):

                explanation.weaknesses.append(reason)

        # =====================================================
        # Observations
        # =====================================================

        if regime.regime == "RANGE":

            explanation.observations.append(
                "Market is trading inside a range."
            )

        elif regime.regime == "TRENDING":

            explanation.observations.append(
                "Trending market detected."
            )

        elif regime.regime == "BREAKOUT":

            explanation.observations.append(
                "Breakout conditions are developing."
            )

        if regime.volatility == "HIGH":

            explanation.warnings.append(
                "High volatility may increase option premiums."
            )

        elif regime.volatility == "LOW":

            explanation.observations.append(
                "Low volatility environment."
            )

        # =====================================================
        # Dealer Interpretation
        # =====================================================

        dealer = snapshot.dealer.get(
            "dealer_gamma",
            "UNKNOWN"
        )

        if dealer == "LONG":

            explanation.observations.append(
                "Dealers are positioned LONG."
            )

        elif dealer == "SHORT":

            explanation.observations.append(
                "Dealers are positioned SHORT."
            )

        # =====================================================
        # Narrative
        # =====================================================

        parts = []

        parts.append(
            f"Market is currently in a {regime.regime} environment."
        )

        dealer = snapshot.dealer.get("dealer_gamma", "UNKNOWN")

        if dealer == "LONG":

            parts.append(
                "Dealers remain LONG, indicating a positive gamma environment."
            )

        elif dealer == "SHORT":

            parts.append(
                "Dealers remain SHORT, increasing directional risk."
            )

        if explanation.confidence < 30:

            parts.append(
                "Current conviction is low."
            )

        elif explanation.confidence < 70:

            parts.append(
                "Market conviction is moderate."
            )

        else:

            parts.append(
                "Market conviction is high."
            )

        if explanation.recommendation == "WAIT":

            parts.append(
                "No high-quality trade setup is currently available."
            )

        elif explanation.recommendation == "BUY CALL":

            parts.append(
                "Bullish conditions support long call opportunities."
            )

        elif explanation.recommendation == "BUY PUT":

            parts.append(
                "Bearish conditions support long put opportunities."
            )

        explanation.narrative = " ".join(parts)

        # =====================================================
        # WHY
        # =====================================================

        for reason in decision.reasons:

            explanation.why.append(reason)

        # =====================================================
        # Future Triggers
        # =====================================================

        if explanation.recommendation == "WAIT":

            explanation.triggers.extend([
                "Institutional strength improves.",
                "Probability score increases.",
                "Trend changes from RANGE to TRENDING.",
                "Spot breaks a key gamma level."
            ])

        # =====================================================
        # Summary
        # =====================================================

        explanation.summary = (
            f"{explanation.recommendation} "
            f"({explanation.confidence}% confidence)"
        )
        return explanation