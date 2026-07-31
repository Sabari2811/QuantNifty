from dataclasses import dataclass


@dataclass
class PerformanceStatistics:
    """
    Aggregated trading performance metrics.
    """

    total_trades: int = 0

    winning_trades: int = 0

    losing_trades: int = 0

    win_rate: float = 0.0

    loss_rate: float = 0.0

    gross_profit: float = 0.0

    gross_loss: float = 0.0

    net_profit: float = 0.0

    average_win: float = 0.0

    average_loss: float = 0.0

    profit_factor: float = 0.0

    expectancy: float = 0.0

    largest_win: float = 0.0

    largest_loss: float = 0.0

    max_drawdown: float = 0.0

    current_drawdown: float = 0.0

    equity_curve: list[float] | None = None