from decision.market_regime import MarketRegime


class MarketRegimeEngine:
    """
    Determines the current market regime.

    Probability input is read from the canonical analytics
    snapshot property. Legacy MarketSnapshot consumers remain
    supported through the snapshot compatibility alias.
    """

    def analyze(self, snapshot):

        regime = MarketRegime()

        dealer = snapshot.dealer
        probability_data = snapshot.probability
        pcr = snapshot.pcr

        dealer_gamma = dealer.get("dealer_gamma", "UNKNOWN")
        probability = self._resolve_probability(
            probability_data
        )
        bias = pcr.get("bias", "NEUTRAL")

        # -------------------------------------
        # Trend
        # -------------------------------------

        if dealer_gamma == "LONG" and bias == "BULLISH":
            regime.trend = "BULLISH"

        elif dealer_gamma == "SHORT" and bias == "BEARISH":
            regime.trend = "BEARISH"

        else:
            regime.trend = "NEUTRAL"

        # -------------------------------------
        # Regime
        # -------------------------------------

        if probability >= 80:
            regime.regime = "TRENDING"

        elif probability >= 60:
            regime.regime = "BREAKOUT"

        else:
            regime.regime = "RANGE"

        # -------------------------------------
        # Volatility
        # -------------------------------------

        atr = snapshot.atr.get("atr", 0)

        if atr >= 250:
            regime.volatility = "HIGH"

        elif atr <= 100:
            regime.volatility = "LOW"

        else:
            regime.volatility = "NORMAL"

        regime.confidence = probability

        return regime

    @staticmethod
    def _resolve_probability(probability_data):
        """Normalize supported probability producer shapes."""
        if isinstance(probability_data, dict):
            for key in (
                "prediction_score",
                "probability",
                "score",
            ):
                value = probability_data.get(key)
                if value is not None:
                    return float(value)
            return 0.0

        if probability_data is None:
            return 0.0

        return float(probability_data)
