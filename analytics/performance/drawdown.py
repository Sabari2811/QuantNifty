class Drawdown:

    def calculate(self, trades):

        equity = 0

        peak = 0

        max_dd = 0

        for trade in trades:

            equity += trade.pnl

            peak = max(
                peak,
                equity
            )

            dd = peak - equity

            max_dd = max(
                max_dd,
                dd
            )

        return round(
            max_dd,
            2
        )