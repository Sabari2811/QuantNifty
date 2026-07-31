class EquityCurve:

    def build(self, trades):

        equity = []

        total = 0

        for trade in trades:

            total += trade.pnl

            equity.append(total)

        return equity