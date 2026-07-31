from decision.market_regime import MarketRegime


class MarketRegimeEngine:
    """
    Determines the current market regime.
    """

    def analyze(self, snapshot):

        regime = MarketRegime()

        dealer = snapshot.dealer
        prediction = snapshot.prediction
        pcr = snapshot.pcr

        dealer_gamma = dealer.get("dealer_gamma", "UNKNOWN")
        probability = prediction.get("prediction_score", 0)
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