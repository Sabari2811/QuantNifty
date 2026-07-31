from __future__ import annotations


class SimilarityScorer:
    """
    Computes weighted similarity score between
    two TradeIntelligenceRecords.
    """

    WEIGHTS = {

        "dealer_gamma":20,

        "dealer_delta":15,

        "trend":15,

        "market_structure":10,

        "gamma_exposure":10,

        "delta_exposure":10,

        "iv_rank":5,

        "pcr":5,

        "adx":5,

        "confidence":5,

    }

    def score(
        self,
        current,
        historical,
    ):

        score = 0

        #
        # Dealer Gamma
        #

        if current.dealer_gamma == historical.dealer_gamma:

            score += self.WEIGHTS["dealer_gamma"]

        #
        # Dealer Delta
        #

        if current.dealer_delta == historical.dealer_delta:

            score += self.WEIGHTS["dealer_delta"]

        #
        # Trend
        #

        if current.trend == historical.trend:

            score += self.WEIGHTS["trend"]

        #
        # Structure
        #

        if current.market_structure == historical.market_structure:

            score += self.WEIGHTS["market_structure"]

        #
        # Numeric Similarity
        #

        score += self._numeric(

            current.gamma_exposure,

            historical.gamma_exposure,

            self.WEIGHTS["gamma_exposure"]

        )

        score += self._numeric(

            current.delta_exposure,

            historical.delta_exposure,

            self.WEIGHTS["delta_exposure"]

        )

        score += self._numeric(

            current.iv_rank,

            historical.iv_rank,

            self.WEIGHTS["iv_rank"]

        )

        score += self._numeric(

            current.pcr,

            historical.pcr,

            self.WEIGHTS["pcr"]

        )

        score += self._numeric(

            current.adx,

            historical.adx,

            self.WEIGHTS["adx"]

        )

        score += self._numeric(

            current.confidence,

            historical.confidence,

            self.WEIGHTS["confidence"]

        )

        return round(score,2)

    def _numeric(
        self,
        a,
        b,
        weight,
    ):

        if a == b:

            return weight

        diff = abs(a-b)

        pct = max(

            0,

            1-(diff/max(abs(a),abs(b),1))

        )

        return weight*pct