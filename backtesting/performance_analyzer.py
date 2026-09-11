from __future__ import annotations

from statistics import mean, stdev

from backtesting.metrics import PerformanceMetrics


class PerformanceAnalyzer:
    """Calculate completed-trade performance statistics.

    Sharpe and Sortino are deliberately *unannualized per-trade* ratios. The
    analyzer does not assume a fixed trading frequency, so annualization would
    otherwise manufacture precision that the replay data does not support.
    """

    def analyze(
        self,
        trades,
        starting_capital: float = 0.0,
    ) -> PerformanceMetrics:
        metrics = PerformanceMetrics()

        if not trades:
            return metrics

        pnl_list = [float(t.pnl) for t in trades]
        wins = [p for p in pnl_list if p > 0]
        losses = [p for p in pnl_list if p < 0]
        breakeven = [p for p in pnl_list if p == 0]

        metrics.total_trades = len(trades)
        metrics.winning_trades = len(wins)
        metrics.losing_trades = len(losses)
        metrics.breakeven_trades = len(breakeven)

        metrics.gross_profit = sum(wins)
        metrics.gross_loss = abs(sum(losses))
        metrics.net_profit = sum(pnl_list)

        metrics.win_rate = metrics.winning_trades / metrics.total_trades * 100
        metrics.loss_rate = metrics.losing_trades / metrics.total_trades * 100

        if wins:
            metrics.average_win = metrics.gross_profit / len(wins)
            metrics.largest_win = max(wins)

        if losses:
            metrics.average_loss = metrics.gross_loss / len(losses)
            metrics.largest_loss = min(losses)

        metrics.expectancy = metrics.net_profit / metrics.total_trades

        if metrics.gross_loss:
            metrics.profit_factor = metrics.gross_profit / metrics.gross_loss

        risk_rewards = [
            float(getattr(t, "risk_reward", 0.0))
            for t in trades
            if float(getattr(t, "risk_reward", 0.0)) > 0
        ]
        if risk_rewards:
            metrics.average_risk_reward = mean(risk_rewards)

        holding_minutes = [
            max(0.0, float(getattr(t, "holding_seconds", 0.0))) / 60.0
            for t in trades
        ]
        if holding_minutes:
            metrics.average_holding_minutes = mean(holding_minutes)

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
            metrics.consecutive_wins = max(metrics.consecutive_wins, current_wins)
            metrics.consecutive_losses = max(metrics.consecutive_losses, current_losses)

        equity = starting_capital
        peak = starting_capital
        max_drawdown = 0.0
        for pnl in pnl_list:
            equity += pnl
            peak = max(peak, equity)
            max_drawdown = max(max_drawdown, peak - equity)

        metrics.max_drawdown = max_drawdown
        metrics.starting_capital = starting_capital
        metrics.ending_capital = equity

        if starting_capital > 0:
            metrics.roi_percent = metrics.net_profit / starting_capital * 100

            # Per-trade returns use the same starting-capital denominator for
            # every observation. This is intentionally not annualized.
            returns = [pnl / starting_capital for pnl in pnl_list]
            if len(returns) >= 2:
                return_std = stdev(returns)
                if return_std > 0:
                    metrics.sharpe_ratio = mean(returns) / return_std

                downside = [value for value in returns if value < 0]
                if len(downside) >= 2:
                    downside_std = stdev(downside)
                    if downside_std > 0:
                        metrics.sortino_ratio = mean(returns) / downside_std

        if metrics.max_drawdown > 0:
            metrics.recovery_factor = metrics.net_profit / metrics.max_drawdown

        return metrics
