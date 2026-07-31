from __future__ import annotations

from backtesting.metrics import PerformanceMetrics


class PerformanceAnalyzer:
    """
    Calculates institutional-grade trading statistics.

    Input
    -----
    TradeJournal.records

    Output
    ------
    PerformanceMetrics
    """

    def analyze(
        self,
        trades,
        starting_capital: float = 0.0,
    ) -> PerformanceMetrics:

        metrics = PerformanceMetrics()

        if not trades:
            return metrics

        # ----------------------------------------------------
        # Basic Trade Lists
        # ----------------------------------------------------

        pnl_list = [t.pnl for t in trades]

        wins = [p for p in pnl_list if p > 0]

        losses = [p for p in pnl_list if p < 0]

        breakeven = [p for p in pnl_list if p == 0]

        # ----------------------------------------------------
        # Counts
        # ----------------------------------------------------

        metrics.total_trades = len(trades)

        metrics.winning_trades = len(wins)

        metrics.losing_trades = len(losses)

        metrics.breakeven_trades = len(breakeven)

        # ----------------------------------------------------
        # Profit
        # ----------------------------------------------------

        metrics.gross_profit = sum(wins)

        metrics.gross_loss = abs(sum(losses))

        metrics.net_profit = sum(pnl_list)

        # ----------------------------------------------------
        # Win / Loss %
        # ----------------------------------------------------

        if metrics.total_trades:

            metrics.win_rate = (
                metrics.winning_trades
                / metrics.total_trades
            ) * 100

            metrics.loss_rate = (
                metrics.losing_trades
                / metrics.total_trades
            ) * 100

        # ----------------------------------------------------
        # Average Winner / Loser
        # ----------------------------------------------------

        if wins:
            metrics.average_win = (
                metrics.gross_profit / len(wins)
            )

            metrics.largest_win = max(wins)

        if losses:
            metrics.average_loss = (
                metrics.gross_loss / len(losses)
            )

            metrics.largest_loss = min(losses)

        # ----------------------------------------------------
        # Expectancy
        # ----------------------------------------------------

        metrics.expectancy = (
            metrics.net_profit
            / metrics.total_trades
            if metrics.total_trades
            else 0.0
        )

        # ----------------------------------------------------
        # Profit Factor
        # ----------------------------------------------------

        if metrics.gross_loss:

            metrics.profit_factor = (
                metrics.gross_profit
                / metrics.gross_loss
            )

        # ----------------------------------------------------
        # Consecutive Wins / Losses
        # ----------------------------------------------------

        current_wins = 0
        current_losses = 0

        for pnl in pnl_list:

            if pnl > 0:

                current_wins += 1

                current_losses = 0

            elif pnl < 0:

                current_losses += 1

                current_wins = 0

            else:

                current_wins = 0
                current_losses = 0

            metrics.consecutive_wins = max(
                metrics.consecutive_wins,
                current_wins,
            )

            metrics.consecutive_losses = max(
                metrics.consecutive_losses,
                current_losses,
            )

        # ----------------------------------------------------
        # Equity Curve
        # ----------------------------------------------------

        equity = starting_capital

        peak = starting_capital

        max_drawdown = 0.0

        for pnl in pnl_list:

            equity += pnl

            peak = max(
                peak,
                equity,
            )

            drawdown = peak - equity

            max_drawdown = max(
                max_drawdown,
                drawdown,
            )

        metrics.max_drawdown = max_drawdown

        metrics.starting_capital = starting_capital

        metrics.ending_capital = equity

        # ----------------------------------------------------
        # ROI
        # ----------------------------------------------------

        if starting_capital > 0:

            metrics.roi_percent = (

                metrics.net_profit

                / starting_capital

            ) * 100

        # ----------------------------------------------------
        # Recovery Factor
        # ----------------------------------------------------

        if metrics.max_drawdown > 0:

            metrics.recovery_factor = (

                metrics.net_profit

                / metrics.max_drawdown

            )

        return metrics