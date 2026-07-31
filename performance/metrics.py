class MetricsCalculator:
    """
    Pure performance calculations.

    No dependency on:
        Broker
        Portfolio
        Journal
        PerformanceEngine
    """

    @staticmethod
    def calculate(trades, capital=500000):

        total = len(trades)

        if total == 0:

            return {

                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "breakeven_trades": 0,

                "win_rate": 0,

                "gross_profit": 0,
                "gross_loss": 0,
                "net_profit": 0,

                "average_win": 0,
                "average_loss": 0,

                "largest_win": 0,
                "largest_loss": 0,

                "profit_factor": 0,
                "expectancy": 0,
                "roi": 0,

            }

        winners = [t for t in trades if t.pnl > 0]
        losers = [t for t in trades if t.pnl < 0]
        breakeven = [t for t in trades if t.pnl == 0]

        gross_profit = sum(t.pnl for t in winners)

        gross_loss = abs(sum(t.pnl for t in losers))

        net_profit = gross_profit - gross_loss

        average_win = (
            gross_profit / len(winners)
            if winners else 0
        )

        average_loss = (
            gross_loss / len(losers)
            if losers else 0
        )

        largest_win = max(
            (t.pnl for t in winners),
            default=0
        )

        largest_loss = min(
            (t.pnl for t in losers),
            default=0
        )

        profit_factor = (
            gross_profit / gross_loss
            if gross_loss > 0
            else float("inf")
        )

        expectancy = net_profit / total

        roi = (
            net_profit / capital
        ) * 100

        return {

            "total_trades": total,

            "winning_trades": len(winners),

            "losing_trades": len(losers),

            "breakeven_trades": len(breakeven),

            "win_rate": (
                len(winners) / total
            ) * 100,

            "gross_profit": gross_profit,

            "gross_loss": gross_loss,

            "net_profit": net_profit,

            "average_win": average_win,

            "average_loss": average_loss,

            "largest_win": largest_win,

            "largest_loss": largest_loss,

            "profit_factor": profit_factor,

            "expectancy": expectancy,

            "roi": roi,

        }