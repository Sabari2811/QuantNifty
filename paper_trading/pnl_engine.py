class PnLEngine:

    def __init__(self, portfolio):

        self.portfolio = portfolio

    # --------------------------------------------
    # Update One Position
    # --------------------------------------------

    def update_price(
        self,
        position,
        current_price,
    ):

        position.current_price = current_price

        position.pnl = (
            current_price
            - position.order.entry_price
        ) * position.order.quantity

    # --------------------------------------------
    # Recalculate Entire Portfolio
    # --------------------------------------------

    def update_portfolio(self):

        self.portfolio.unrealized_pnl = sum(

            position.pnl

            for position in self.portfolio.open_positions

            if not position.closed

        )

    # --------------------------------------------
    # Portfolio Value
    # --------------------------------------------

    def portfolio_value(self):

        return (

            self.portfolio.capital

            + self.portfolio.realized_pnl

            + self.portfolio.unrealized_pnl

        )