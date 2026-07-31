from performance.metrics import MetricsCalculator
from performance.equity import EquityCurve
from performance.drawdown import DrawdownCalculator
from performance.models import PerformanceMetrics


class PerformanceEngine:
    """
    High-level orchestrator for
    all performance analytics.
    """

    def __init__(self, journal):

        self.journal = journal

    def calculate(self):

        trades = self.journal.all_trades()

        values = MetricsCalculator.calculate(
            trades
        )

        equity = EquityCurve.build(
            trades
        )

        risk = DrawdownCalculator.calculate(
            equity
        )

        values.update(risk)

        return PerformanceMetrics(
            **values
        )