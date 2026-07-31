from dataclasses import dataclass


@dataclass
class Portfolio:
    """
    Represents the current paper portfolio.
    """

    initial_capital: float = 500000

    available_cash: float = 500000

    margin_used: float = 0

    realized_pnl: float = 0

    unrealized_pnl: float = 0

    total_equity: float = 500000

    total_trades: int = 0

    open_positions: int = 0