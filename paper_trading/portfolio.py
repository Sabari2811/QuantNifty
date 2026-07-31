from paper_trading.models import Portfolio


class PortfolioEngine:
    """
    Manages the paper trading portfolio.

    Responsible for:
    - Maintaining portfolio balances
    - Tracking open positions
    - Tracking closed positions

    Does NOT:
    - Execute orders
    - Calculate MTM
    - Calculate P&L
    """

    def __init__(self):

        self.portfolio = Portfolio()

    # -------------------------------------------------
    # Add Position
    # -------------------------------------------------

    def add_position(self, position, investment):

        self.portfolio.available_cash -= investment

        self.portfolio.invested_amount += investment

        self.portfolio.open_positions.append(position)

    # -------------------------------------------------
    # Portfolio Summary
    # -------------------------------------------------

    def summary(self):

        return {

            "capital": self.portfolio.capital,

            "available_cash": self.portfolio.available_cash,

            "invested_amount": self.portfolio.invested_amount,

            "realized_pnl": self.portfolio.realized_pnl,

            "unrealized_pnl": self.portfolio.unrealized_pnl,

            "open_positions": len(
                self.portfolio.open_positions
            ),

            "closed_positions": len(
                self.portfolio.closed_positions
            )

        }