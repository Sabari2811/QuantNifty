class MarketMap:

    """
    Decision object representing the important
    market levels for the trading terminal.
    """

    def __init__(self):

        self.spot = None

        self.dealer = "-"

        self.gamma_flip = "-"

        self.gamma_wall = "-"

        self.call_wall = "-"

        self.put_wall = "-"

        self.max_pain = "-"

        self.expected_move = "-"

    @classmethod
    def from_analytics(

        cls,

        analytics

    ):

        obj = cls()

        data = analytics.get(
            "market_map",
            {}
        )

        obj.spot = data.get(
            "spot"
        )

        obj.dealer = data.get(
            "dealer_gamma"
        )

        obj.gamma_flip = data.get(
            "gamma_flip"
        )

        obj.gamma_wall = data.get(
            "gamma_wall"
        )

        obj.call_wall = data.get(
            "call_wall"
        )

        obj.put_wall = data.get(
            "put_wall"
        )

        obj.max_pain = data.get(
            "max_pain"
        )

        obj.expected_move = data.get(
            "expected_move"
        )

        return obj