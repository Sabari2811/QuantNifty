from paper_trading.execution_adapter import PaperBroker
from paper_trading.position_manager import PositionManager
from paper_trading.portfolio_manager import PortfolioManager
from paper_trading.trade_book import TradeBook
from paper_trading.statistics_engine import StatisticsEngine


class PaperEngine:
    """
    Orchestrates paper trading.
    """

    def __init__(self):

        self.broker = PaperBroker()

        self.positions = PositionManager()

        self.portfolio = PortfolioManager()

        self.trade_book = TradeBook()

        self.statistics = StatisticsEngine()