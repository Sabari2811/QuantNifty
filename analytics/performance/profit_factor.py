class ProfitFactor:
    """
    Calculates profit metrics.
    """

    def calculate(self, trades):

        gross_profit = sum(

            trade.pnl

            for trade in trades

            if trade.pnl > 0

        )

        gross_loss = abs(sum(

            trade.pnl

            for trade in trades

            if trade.pnl < 0

        ))

        average_win = 0.0

        average_loss = 0.0

        winners = [

            t.pnl

            for t in trades

            if t.pnl > 0

        ]

        losers = [

            abs(t.pnl)

            for t in trades

            if t.pnl < 0

        ]

        if winners:

            average_win = round(

                sum(winners) / len(winners),

                2

            )

        if losers:

            average_loss = round(

                sum(losers) / len(losers),

                2

            )

        profit_factor = 0.0

        if gross_loss > 0:

            profit_factor = round(

                gross_profit / gross_loss,

                2

            )

        return {

            "gross_profit": round(gross_profit, 2),

            "gross_loss": round(gross_loss, 2),

            "average_win": average_win,

            "average_loss": average_loss,

            "profit_factor": profit_factor

        }