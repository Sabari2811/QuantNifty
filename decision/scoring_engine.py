from config.trading_config import TradingConfig


class ScoringEngine:
    """
    Institutional weighted scoring engine.

    Produces a score together with
    a detailed score breakdown.
    """

    def score(self, market):

        score = 0

        reasons = []

        breakdown = {}

        # ----------------------------------
        # Dealer
        # ----------------------------------

        dealer_score = 0

        if market.dealer == "LONG":

            dealer_score = TradingConfig.DEALER_LONG_SCORE

            reasons.append("Dealer LONG")

        elif market.dealer == "SHORT":

            dealer_score = TradingConfig.DEALER_SHORT_SCORE

            reasons.append("Dealer SHORT")

        breakdown["dealer"] = dealer_score

        score += dealer_score

        # ----------------------------------
        # Gamma
        # ----------------------------------

        gamma_score = 0

        if market.gamma_state == "POSITIVE":

            gamma_score = TradingConfig.GAMMA_POSITIVE_SCORE

            reasons.append("Positive Gamma")

        elif market.gamma_state == "NEGATIVE":

            gamma_score = TradingConfig.GAMMA_NEGATIVE_SCORE

            reasons.append("Negative Gamma")

        breakdown["gamma"] = gamma_score

        score += gamma_score

        # ----------------------------------
        # PCR
        # ----------------------------------

        pcr_score = 0

        if market.pcr_bias == "BULLISH":

            pcr_score = TradingConfig.PCR_BULLISH_SCORE

            reasons.append("PCR Bullish")

        elif market.pcr_bias == "BEARISH":

            pcr_score = TradingConfig.PCR_BEARISH_SCORE

            reasons.append("PCR Bearish")

        breakdown["pcr"] = pcr_score

        score += pcr_score

        # ----------------------------------
        # Institutional
        # ----------------------------------

        institutional_score = 0

        if market.institutional == "STRONG":

            institutional_score = TradingConfig.INSTITUTION_STRONG_SCORE

            reasons.append("Institution Buying")

        elif market.institutional == "WEAK":

            institutional_score = TradingConfig.INSTITUTION_WEAK_SCORE

            reasons.append("Weak Institution")

        breakdown["institutional"] = institutional_score

        score += institutional_score

        # ----------------------------------
        # Probability
        # ----------------------------------

        probability_score = 0

        if market.probability >= TradingConfig.HIGH_PROBABILITY_THRESHOLD:

            probability_score = TradingConfig.PROBABILITY_HIGH_SCORE

            reasons.append("High Probability")

        elif market.probability <= TradingConfig.LOW_PROBABILITY_THRESHOLD:

            probability_score = TradingConfig.PROBABILITY_LOW_SCORE

            reasons.append("Low Probability")

        breakdown["probability"] = probability_score

        score += probability_score

        # ----------------------------------
        # Final
        # ----------------------------------

        breakdown["total"] = score

        return {

            "score": score,

            "reasons": reasons,

            "breakdown": breakdown

        }