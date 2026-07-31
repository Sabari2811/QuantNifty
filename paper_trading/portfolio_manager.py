from paper_trading.models.portfolio import Portfolio


class PortfolioManager:
    """
    Maintains portfolio state.
    """

    def __init__(self):

        self.portfolio = Portfolio()

    def get(self):

        return self.portfolio