class MarketContextEngine:
    """
    QuantNifty Market Context Engine

    Produces one object describing
    the complete market.
    """

    def build(

        self,

        dealer,

        probability,

        atr,

        signal

    ):

        context = {

            "dealer_gamma": dealer["dealer_gamma"],

            "market_mode": dealer["market_mode"],

            "volatility": atr["volatility"],

            "atr": atr["atr"],

            "bullish_probability":

                probability["bullish_probability"],

            "bearish_probability":

                probability["bearish_probability"],

            "confidence":

                probability["confidence"],

            "signal":

                signal["signal"]

        }

        return context