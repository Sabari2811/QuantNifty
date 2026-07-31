from dataclasses import dataclass


@dataclass(frozen=True)
class PerformanceMetrics:
    """
    Complete trading performance metrics.
    """

    # Trade Statistics
    total_trades: int
    winning_trades: int
    losing_trades: int
    breakeven_trades: int
    win_rate: float

    # Profitability
    gross_profit: float
    gross_loss: float
    net_profit: float

    average_win: float
    average_loss: float

    largest_win: float
    largest_loss: float

    profit_factor: float
    expectancy: float
    roi: float

    # Risk
    max_drawdown: float
    current_drawdown: float
    peak_equity: float
    ending_equity: float