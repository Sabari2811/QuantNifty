from datetime import datetime

from paper_trading.models import TradeRecord


class PositionMonitor:
    """
    Monitors all live positions.

    Responsibilities:
        - Update LTP
        - Calculate MTM
        - Calculate Unrealized P&L
        - Check SL
        - Check Target
        - Close completed trades
        - Update Portfolio
        - Create Trade Journal record
    """

    def __init__(self, portfolio_engine):

        self.portfolio_engine = portfolio_engine

    # =====================================================
    # MAIN
    # =====================================================

    def update(self, option_chain):

        portfolio = self.portfolio_engine.portfolio

        portfolio.unrealized_pnl = 0

        for position in list(portfolio.open_positions):

            ltp = self._get_ltp(position, option_chain)

            if ltp is None:
                continue

            position.current_price = ltp

            position.pnl = (
                ltp - position.order.entry_price
            ) * position.order.quantity

            portfolio.unrealized_pnl += position.pnl

            if self._should_exit(position):

                self._close_position(position)

    # =====================================================
    # MARKET PRICE
    # =====================================================

    def _get_ltp(self, position, option_chain):

        for row in option_chain:

            if (
                row["strike"] == position.order.strike
                and row["option_type"] == position.order.option_type
            ):
                return row["ltp"]

        return None

    # =====================================================
    # EXIT CHECK
    # =====================================================

    def _should_exit(self, position):

        if position.current_price <= position.stop_loss:
            return True

        if position.current_price >= position.target:
            return True

        return False

    # =====================================================
    # CLOSE
    # =====================================================

    def _close_position(self, position):

        portfolio = self.portfolio_engine.portfolio

        position.closed = True

        position.exit_price = position.current_price

        position.exit_time = datetime.now()

        portfolio.realized_pnl += position.pnl

        portfolio.available_cash += (
            position.current_price
            * position.order.quantity
        )

        portfolio.invested_amount -= (
            position.order.entry_price
            * position.order.quantity
        )

        portfolio.closed_positions.append(position)

        portfolio.open_positions.remove(position)