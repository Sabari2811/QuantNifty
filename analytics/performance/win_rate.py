class WinRate:
    """
    Calculates trade win/loss statistics.
    """

    def calculate(self, trades):

        total = len(trades)

        if total == 0:

            return {

                "winning_trades": 0,

                "losing_trades": 0,

                "win_rate": 0.0,

                "loss_rate": 0.0

            }

        winning = sum(

            1

            for trade in trades

            if trade.pnl > 0

        )

        losing = total - winning

        return {

            "winning_trades": winning,

            "losing_trades": losing,

            "win_rate": round(

                (winning / total) * 100,

                2

            ),

            "loss_rate": round(

                (losing / total) * 100,

                2

            )

        }