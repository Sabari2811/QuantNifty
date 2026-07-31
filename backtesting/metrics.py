from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class PerformanceMetrics:
    """
    Immutable performance statistics produced after a
    completed backtest or replay session.

    This class intentionally contains no calculations.
    It is simply a container for statistics.
    """

    # ----------------------------------------
    # Trade Counts
    # ----------------------------------------

    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    breakeven_trades: int = 0

    # ----------------------------------------
    # Profitability
    # ----------------------------------------

    gross_profit: float = 0.0
    gross_loss: float = 0.0
    net_profit: float = 0.0

    # ----------------------------------------
    # Ratios
    # ----------------------------------------

    win_rate: float = 0.0
    loss_rate: float = 0.0
    expectancy: float = 0.0
    profit_factor: float = 0.0

    # ----------------------------------------
    # Trade Quality
    # ----------------------------------------

    average_win: float = 0.0
    average_loss: float = 0.0

    largest_win: float = 0.0
    largest_loss: float = 0.0

    average_risk_reward: float = 0.0

    # ----------------------------------------
    # Drawdown
    # ----------------------------------------

    max_drawdown: float = 0.0

    recovery_factor: float = 0.0

    # ----------------------------------------
    # Risk Metrics
    # ----------------------------------------

    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0

    # ----------------------------------------
    # Consistency
    # ----------------------------------------

    consecutive_wins: int = 0
    consecutive_losses: int = 0

    # ----------------------------------------
    # Time
    # ----------------------------------------

    average_holding_minutes: float = 0.0

    # ----------------------------------------
    # Capital
    # ----------------------------------------

    starting_capital: float = 0.0
    ending_capital: float = 0.0

    roi_percent: float = 0.0