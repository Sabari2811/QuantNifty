from datetime import datetime
from uuid import uuid4

from paper_trading.models import PaperOrder, PaperPosition
from paper_trading.portfolio import PortfolioEngine
from paper_trading.journal import TradeJournal
from analytics.performance.performance_engine import PerformanceEngine


class PaperBroker:
    """
    Simulates a paper trading broker.

    Responsibilities
    ----------------
    - Execute validated trades
    - Capital checks
    - Prevent duplicate positions
    - Monitor live positions
    - Close positions
    - Record completed trades
    """

    def __init__(self):
        self.portfolio_engine = PortfolioEngine()
        self.journal = TradeJournal()

        self.performance_engine = PerformanceEngine()
        self.performance_statistics = None

    @property
    def portfolio(self):
        return self.portfolio_engine.portfolio

    @property
    def position(self):
        return self.portfolio.open_positions[0] if self.portfolio.open_positions else None

    @property
    def last_trade(self):
        return self.portfolio.closed_positions[-1] if self.portfolio.closed_positions else None

    @property
    def performance(self):
        return self.performance_statistics

    def execute(self, decision):
        if decision is None or not decision.valid:
            return None

        trade = decision.trade
        execution = trade.execution

        investment = execution.lot_size * execution.lots * trade.entry

        if investment > self.portfolio.available_cash:
            print("PaperBroker: Insufficient capital.")
            return None

        for pos in self.portfolio.open_positions:
            if (
                not pos.closed
                and pos.order.strike == trade.strike
                and pos.order.option_type == trade.option_type
            ):
                print("PaperBroker: Position already exists.")
                return None

        order = PaperOrder(
            order_id=str(uuid4()),
            signal=decision.signal.name,
            option_type=trade.option_type,
            strike=trade.strike,
            quantity=execution.lot_size * execution.lots,
            entry_price=trade.entry,
        )

        position = PaperPosition(
            order=order,
            current_price=trade.entry,
            stop_loss=trade.stop_loss,
            target=trade.target1,
            confidence=getattr(decision, "confidence", 0.0),
            risk_reward=getattr(trade, "risk_reward", 0.0),
            strategy_name=getattr(decision, "strategy_name", ""),
        )

        self.portfolio_engine.add_position(position, investment)

        print(f"PaperBroker: Opened {trade.option_type} {trade.strike}")
        return position

    def update_positions(self, option_chain):
        self.portfolio.unrealized_pnl = 0

        for position in list(self.portfolio.open_positions):
            ltp = self._find_ltp(
                option_chain,
                position.order.strike,
                position.order.option_type,
            )

            if ltp is None:
                continue

            position.current_price = ltp
            position.pnl = (
                ltp - position.order.entry_price
            ) * position.order.quantity

            self.portfolio.unrealized_pnl += position.pnl

            if ltp <= position.stop_loss:
                self.close_position(position, ltp, "STOP_LOSS")
                continue

            if ltp >= position.target:
                self.close_position(position, ltp, "TARGET")

    def _find_ltp(self, option_chain, strike, option_type):
        if option_chain is None:
            return None

        if hasattr(option_chain, "iterrows"):
            for _, row in option_chain.iterrows():
                if row["strike"] == strike and row["option_type"] == option_type:
                    return row["ltp"]
            return None

        for row in option_chain:
            if row["strike"] == strike and row["option_type"] == option_type:
                return row["ltp"]

        return None

    def close_position(self, position, exit_price, reason="MANUAL"):
        if position.closed:
            return position

        qty = position.order.quantity
        investment = position.order.entry_price * qty

        position.closed = True
        position.order.status = "CLOSED"
        position.exit_price = exit_price
        position.exit_time = datetime.now()
        position.current_price = exit_price
        position.pnl = (exit_price - position.order.entry_price) * qty

        self.portfolio.available_cash += investment + position.pnl
        self.portfolio.invested_amount -= investment
        self.portfolio.realized_pnl += position.pnl

        if position in self.portfolio.open_positions:
            self.portfolio.open_positions.remove(position)

        self.portfolio.closed_positions.append(position)

        self.portfolio.unrealized_pnl = sum(
            p.pnl for p in self.portfolio.open_positions if not p.closed
        )

        self.journal.record(position, reason)

        # Refresh performance statistics
        self.performance_statistics = self.performance_engine.analyze(
            self.journal.records
        )

        print(f"PaperBroker: Position closed ({reason})")

        return position
