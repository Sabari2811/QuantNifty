class Checklist:

    """
    Trading checklist used by the
    QuantNifty Terminal.
    """

    def __init__(self):

        self.items = []

    @classmethod
    def from_analytics(

        cls,

        analytics,

        spot

    ):

        obj = cls()

        technical = analytics.get(
            "technical",
            {}
        )

        ema = technical.get(
            "ema",
            {}
        )

        vwap = technical.get(
            "vwap",
            {}
        )

        dealer = analytics.get(
            "dealer",
            {}
        )

        pcr = analytics.get(
            "pcr",
            {}
        )

        market_map = analytics.get(
            "market_map",
            {}
        )

        # -----------------------------
        # EMA20
        # -----------------------------

        ema20 = ema.get(
            "ema20",
            spot
        )

        obj.items.append(

            {

                "name": "EMA20",

                "status": "ABOVE"
                if spot > ema20
                else "BELOW"

            }

        )

        # -----------------------------
        # VWAP
        # -----------------------------

        vwap_price = vwap.get(
            "vwap",
            spot
        )

        obj.items.append(

            {

                "name": "VWAP",

                "status": "ABOVE"
                if spot > vwap_price
                else "BELOW"

            }

        )

        # -----------------------------
        # Gamma Flip
        # -----------------------------

        flip = market_map.get(
            "gamma_flip",
            spot
        )

        obj.items.append(

            {

                "name": "Gamma Flip",

                "status": "ABOVE"
                if spot > flip
                else "BELOW"

            }

        )

        # -----------------------------
        # Dealer
        # -----------------------------

        obj.items.append(

            {

                "name": "Dealer",

                "status": dealer.get(
                    "dealer_gamma",
                    "-"
                )

            }

        )

        # -----------------------------
        # PCR
        # -----------------------------

        value = pcr.get(
            "oi_pcr",
            1
        )

        obj.items.append(

            {

                "name": "PCR",

                "status": "BULLISH"
                if value >= 1
                else "BEARISH"

            }

        )

        return obj