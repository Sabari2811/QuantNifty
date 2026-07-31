import pandas as pd


class MarketStructureEngine:
    """
    Market Structure Classification
    """

    def analyze(
        self,
        greeks_df: pd.DataFrame,
        dealer: dict,
        pcr: dict,
        expected_move: dict
    ):

        if greeks_df.empty:

            return {

                "structure": "UNKNOWN",

                "bias": "NEUTRAL",

                "confidence": 0,

                "reason": "No Data"

            }

        spot = dealer["spot"]

        flip = dealer["gamma_flip"]

        resistance = dealer["resistance"]

        support = dealer["support"]

        bullish = 0
        bearish = 0

        # ----------------------------------
        # Dealer Gamma
        # ----------------------------------

        if dealer["dealer_gamma"] == "LONG":
            bullish += 1
        else:
            bearish += 1

        # ----------------------------------
        # PCR
        # ----------------------------------

        if pcr["oi_pcr"] > 1:
            bullish += 1
        else:
            bearish += 1

        # ----------------------------------
        # Gamma Flip
        # ----------------------------------

        if flip is not None:

            if spot > flip:
                bullish += 1
            else:
                bearish += 1

        # ----------------------------------
        # Expected Move
        # ----------------------------------

        if spot >= expected_move["upper"]:

            return {

                "structure": "BREAKOUT",

                "bias": "BULLISH",

                "confidence": 90,

                "reason": "Above Expected Move"

            }

        if spot <= expected_move["lower"]:

            return {

                "structure": "BREAKDOWN",

                "bias": "BEARISH",

                "confidence": 90,

                "reason": "Below Expected Move"

            }

        # ----------------------------------
        # Trend Decision
        # ----------------------------------

        if bullish >= bearish + 2:

            return {

                "structure": "TRENDING_UP",

                "bias": "BULLISH",

                "confidence": bullish * 20,

                "reason": "Dealer + PCR + Gamma"

            }

        if bearish >= bullish + 2:

            return {

                "structure": "TRENDING_DOWN",

                "bias": "BEARISH",

                "confidence": bearish * 20,

                "reason": "Dealer + PCR + Gamma"

            }

        return {

            "structure": "RANGING",

            "bias": "NEUTRAL",

            "confidence": 50,

            "reason": "Mixed Signals"

        }