class TradeBook:
    """
    Stores completed paper trades.
    """

    def __init__(self):

        self.trades = []

    def add(self, trade):

        self.trades.append(trade)

    def all(self):

        return self.trades