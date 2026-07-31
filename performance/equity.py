class EquityCurve:
    """
    Builds account equity after each completed trade.
    """

    @staticmethod
    def build(
        trades,
        capital=500000
    ):

        equity = [capital]

        running = capital

        for trade in trades:

            running += trade.pnl

            equity.append(running)

        return equity