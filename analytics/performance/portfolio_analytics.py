class PortfolioAnalytics:
    """
    Portfolio performance analytics.

    Responsibility:
    - Equity Curve
    - Running Equity
    - Peak Equity
    - Portfolio Growth
    """

    def analyze(self, trades):
        """
        Analyze portfolio performance.

        Args:
            trades (list): List of completed Trade objects.

        Returns:
            dict
        """

        if not trades:
            return {
                "equity_curve": [],
                "running_equity": 0.0,
                "peak_equity": 0.0,
                "portfolio_growth": 0.0,
            }

        equity_curve = []

        running_equity = 0.0

        peak_equity = 0.0

        for trade in trades:

            running_equity += trade.pnl

            equity_curve.append(
                round(running_equity, 2)
            )

            peak_equity = max(
                peak_equity,
                running_equity
            )

        portfolio_growth = running_equity

        return {

            "equity_curve": equity_curve,

            "running_equity": round(
                running_equity,
                2
            ),

            "peak_equity": round(
                peak_equity,
                2
            ),

            "portfolio_growth": round(
                portfolio_growth,
                2
            ),

        }