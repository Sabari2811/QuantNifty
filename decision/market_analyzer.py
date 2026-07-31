from decision.market_context import MarketContext


class MarketAnalyzer:
    """
    Converts MarketSnapshot into MarketContext.

    Responsible ONLY for understanding
    the current market.
    """

    def analyze(self, snapshot):

        market = MarketContext()

        # ==================================================
        # Dealer
        # ==================================================

        dealer = snapshot.dealer

        market.dealer = dealer.get(
            "dealer_gamma",
            "UNKNOWN"
        )

        # ==================================================
        # Gamma Levels
        # ==================================================

        market.gamma_flip = dealer.get(
            "gamma_flip"
        )

        market.gamma_wall = dealer.get(
            "gamma_wall"
        )

        market.call_wall = dealer.get(
            "call_wall"
        )

        market.put_wall = dealer.get(
            "put_wall"
        )

        if market.gamma_flip is not None:

            if snapshot.spot > market.gamma_flip:

                market.gamma_state = "POSITIVE"

            else:

                market.gamma_state = "NEGATIVE"

        # ==================================================
        # PCR
        # ==================================================

        market.pcr_bias = snapshot.pcr.get(
            "bias",
            "UNKNOWN"
        )

        # ==================================================
        # Institutional
        # ==================================================

        inst = snapshot.institutional.get(
            "institutional",
            {}
        )

        score = inst.get(
            "score",
            0
        )

        if score >= 70:

            market.institutional = "STRONG"

        elif score >= 40:

            market.institutional = "MODERATE"

        else:

            market.institutional = "WEAK"

        # ==================================================
        # Probability
        # ==================================================

        market.probability = snapshot.prediction.get(
            "prediction_score",
            0
        )

        # ==================================================
        # Expected Move
        # ==================================================

        market.expected_move = snapshot.expected_move.get(
            "expected_move",
            0
        )

        # ==================================================
        # Max Pain
        # ==================================================

        market.max_pain = snapshot.max_pain.get(
            "max_pain"
        )

        # ==================================================
        # Volatility
        # ==================================================

        atr = snapshot.atr.get(
            "atr",
            0
        )

        market.atr = atr

        if atr >= 250:

            market.volatility = "HIGH"

        elif atr >= 120:

            market.volatility = "NORMAL"

        else:

            market.volatility = "LOW"

        # ==================================================
        # Liquidity
        # ==================================================

        market.liquidity = "NORMAL"

        # ==================================================
        # Regime
        # ==================================================

        bullish = 0
        bearish = 0

        if market.dealer == "LONG":
            bullish += 1
        elif market.dealer == "SHORT":
            bearish += 1

        if market.gamma_state == "POSITIVE":
            bullish += 1
        elif market.gamma_state == "NEGATIVE":
            bearish += 1

        if market.pcr_bias == "BULLISH":
            bullish += 1
        elif market.pcr_bias == "BEARISH":
            bearish += 1

        if market.institutional == "STRONG":
            bullish += 1
        elif market.institutional == "WEAK":
            bearish += 1

        if bullish >= 3:

            market.regime = "TRENDING"

            market.bias = "BULLISH"

        elif bearish >= 3:

            market.regime = "TRENDING"

            market.bias = "BEARISH"

        else:

            market.regime = "RANGE"

            market.bias = "NEUTRAL"

        return market