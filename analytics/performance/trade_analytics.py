class TradeAnalytics:
    """
    Calculates trade performance statistics.

    Responsibility:
    - Trade counts
    - Win/Loss ratio
    - Average Win/Loss
    - Largest Win/Loss

    This class is independent of:
    - PaperBroker
    - RuntimeContext
    - Dashboard
    - Database
    """

    def analyze(self, trades):
        """
        Analyze completed trades.

        Args:
            trades (list): List of completed Trade objects.

        Returns:
            dict
        """

        total_trades = len(trades)

        if total_trades == 0:
            return {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0.0,
                "loss_rate": 0.0,
                "average_win": 0.0,
                "average_loss": 0.0,
                "largest_win": 0.0,
                "largest_loss": 0.0,
            }

        winners = [trade.pnl for trade in trades if trade.pnl > 0]
        losers = [abs(trade.pnl) for trade in trades if trade.pnl < 0]

        winning_trades = len(winners)
        losing_trades = len(losers)

        average_win = (
            sum(winners) / winning_trades
            if winning_trades
            else 0.0
        )

        average_loss = (
            sum(losers) / losing_trades
            if losing_trades
            else 0.0
        )

        return {

            "total_trades": total_trades,

            "winning_trades": winning_trades,

            "losing_trades": losing_trades,

            "win_rate": round(
                (winning_trades / total_trades) * 100,
                2
            ),

            "loss_rate": round(
                (losing_trades / total_trades) * 100,
                2
            ),

            "average_win": round(
                average_win,
                2
            ),

            "average_loss": round(
                average_loss,
                2
            ),

            "largest_win": round(
                max(winners),
                2
            ) if winners else 0.0,

            "largest_loss": round(
                max(losers),
                2
            ) if losers else 0.0,

        }