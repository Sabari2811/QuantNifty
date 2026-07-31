class MarketMapEngine:

    """
    Produces the important market levels
    required by the QuantNifty Terminal.
    """

    def build(

        self,

        analytics,

        spot

    ):

        dealer = analytics.get(
            "dealer",
            {}
        )

        gamma = analytics.get(
            "gamma_levels",
            {}
        )

        expected = analytics.get(
            "expected_move",
            {}
        )

        max_pain = analytics.get(
            "max_pain",
            {}
        )

        return {

            "spot": round(spot, 2),

            "dealer_gamma": dealer.get(
                "dealer_gamma",
                "-"
            ),

            "gamma_flip": gamma.get(
                "gamma_flip",
                "-"
            ),

            "gamma_wall": gamma.get(
                "gamma_wall",
                "-"
            ),

            "call_wall": gamma.get(
                "call_wall",
                "-"
            ),

            "put_wall": gamma.get(
                "put_wall",
                "-"
            ),

            "max_pain": max_pain.get(
                "max_pain",
                "-"
            ),

            "expected_move": expected.get(
                "expected_move",
                "-"
            )

        }