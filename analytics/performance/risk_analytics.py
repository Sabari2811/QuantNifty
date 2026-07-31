class RiskAnalytics:
    """
    Risk and profitability analytics.

    Responsibility:
    - Gross Profit
    - Gross Loss
    - Net Profit
    - Profit Factor
    - Expectancy
    - Maximum Drawdown
    - Current Drawdown
    """

    def analyze(self, trades):
        """
        Analyze completed trades.

        Args:
            trades (list): List of completed Trade objects.

        Returns:
            dict
        """

        if not trades:
            return {
                "gross_profit": 0.0,
                "gross_loss": 0.0,
                "net_profit": 0.0,
                "profit_factor": 0.0,
                "expectancy": 0.0,
                "max_drawdown": 0.0,
                "current_drawdown": 0.0,
            }

        winners = [trade.pnl for trade in trades if trade.pnl > 0]
        losers = [abs(trade.pnl) for trade in trades if trade.pnl < 0]

        gross_profit = sum(winners)
        gross_loss = sum(losers)
        net_profit = gross_profit - gross_loss

        average_win = (
            gross_profit / len(winners)
            if winners else 0.0
        )

        average_loss = (
            gross_loss / len(losers)
            if losers else 0.0
        )

        win_rate = (
            len(winners) / len(trades)
        ) if trades else 0.0

        loss_rate = (
            len(losers) / len(trades)
        ) if trades else 0.0

        expectancy = (
            (win_rate * average_win)
            -
            (loss_rate * average_loss)
        )

        if gross_loss == 0:
            profit_factor = float("inf") if gross_profit > 0 else 0.0
        else:
            profit_factor = gross_profit / gross_loss

        equity = 0.0
        peak = 0.0
        max_drawdown = 0.0
        current_drawdown = 0.0

        for trade in trades:

            equity += trade.pnl

            if equity > peak:
                peak = equity

            drawdown = peak - equity

            if drawdown > max_drawdown:
                max_drawdown = drawdown

            current_drawdown = drawdown

        return {

            "gross_profit": round(gross_profit, 2),

            "gross_loss": round(gross_loss, 2),

            "net_profit": round(net_profit, 2),

            "profit_factor": (
                round(profit_factor, 2)
                if profit_factor != float("inf")
                else float("inf")
            ),

            "expectancy": round(expectancy, 2),

            "max_drawdown": round(max_drawdown, 2),

            "current_drawdown": round(current_drawdown, 2),

        }