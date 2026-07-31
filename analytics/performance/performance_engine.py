from analytics.performance.statistics import PerformanceStatistics
from analytics.performance.trade_analytics import TradeAnalytics
from analytics.performance.risk_analytics import RiskAnalytics
from analytics.performance.portfolio_analytics import PortfolioAnalytics


class PerformanceEngine:
    """
    Orchestrates all performance analytics.

    Pipeline:

        Trades
           │
           ▼
    TradeAnalytics
           │
    RiskAnalytics
           │
    PortfolioAnalytics
           │
           ▼
    PerformanceStatistics
    """

    def __init__(self):

        self.trade_analytics = TradeAnalytics()

        self.risk_analytics = RiskAnalytics()

        self.portfolio_analytics = PortfolioAnalytics()

    def analyze(self, trades):

        stats = PerformanceStatistics()

        trade_metrics = self.trade_analytics.analyze(trades)

        risk_metrics = self.risk_analytics.analyze(trades)

        portfolio_metrics = self.portfolio_analytics.analyze(trades)

        # ----------------------------
        # Trade Metrics
        # ----------------------------

        stats.total_trades = trade_metrics["total_trades"]

        stats.winning_trades = trade_metrics["winning_trades"]

        stats.losing_trades = trade_metrics["losing_trades"]

        stats.win_rate = trade_metrics["win_rate"]

        stats.loss_rate = trade_metrics["loss_rate"]

        stats.average_win = trade_metrics["average_win"]

        stats.average_loss = trade_metrics["average_loss"]

        stats.largest_win = trade_metrics["largest_win"]

        stats.largest_loss = trade_metrics["largest_loss"]

        # ----------------------------
        # Risk Metrics
        # ----------------------------

        stats.gross_profit = risk_metrics["gross_profit"]

        stats.gross_loss = risk_metrics["gross_loss"]

        stats.net_profit = risk_metrics["net_profit"]

        stats.profit_factor = risk_metrics["profit_factor"]

        stats.expectancy = risk_metrics["expectancy"]

        stats.max_drawdown = risk_metrics["max_drawdown"]

        stats.current_drawdown = risk_metrics["current_drawdown"]

        # ----------------------------
        # Portfolio Metrics
        # ----------------------------

        stats.equity_curve = portfolio_metrics["equity_curve"]

        return stats