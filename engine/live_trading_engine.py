import time
from datetime import datetime

from analytics.analytics_pipeline import AnalyticsPipeline
from decision.decision_engine import DecisionEngine
from paper_trading.broker import PaperBroker


class LiveTradingEngine:
    """
    QuantNifty Live Paper Trading Engine

    Responsibilities
    ----------------
    1. Fetch Live Market Data
    2. Run Analytics
    3. Build Trading Decision
    4. Execute Paper Trade
    5. Repeat until market close

    No business logic belongs here.
    """

    def __init__(
        self,
        provider,
        option_chain_manager,
        greeks_engine,
        runtime_config,
    ):

        self.provider = provider
        self.option_chain = option_chain_manager
        self.greeks_engine = greeks_engine
        self.runtime_config = runtime_config

        self.analytics = AnalyticsPipeline()
        self.decision = DecisionEngine()
        self.paper_broker = PaperBroker()

    # -------------------------------------------------------
    # Initialize
    # -------------------------------------------------------

    def initialize(self):

        print("=" * 60)
        print("QUANTNIFTY LIVE PAPER TRADING")
        print("=" * 60)

        self.provider.connect()

        print("Initialization Complete\n")

    # -------------------------------------------------------
    # One Market Cycle
    # -------------------------------------------------------

    def process_market(self):

        symbol = self.runtime_config.symbol

        print("-" * 60)
        print(datetime.now())
        print("-" * 60)

        # ---------------------------------------------------
        # Spot
        # ---------------------------------------------------

        spot = self.provider.get_spot_price(symbol)

        print(f"Spot : {spot}")

        # ---------------------------------------------------
        # Option Chain
        # ---------------------------------------------------

        option_chain = self.option_chain.get_live_option_chain(
            symbol=symbol,
            spot_price=spot,
            levels=self.runtime_config.option_levels,
        )

        # ---------------------------------------------------
        # Greeks
        # ---------------------------------------------------

        greeks_df = self.greeks_engine.calculate(
            option_chain
        )

        # ---------------------------------------------------
        # Analytics
        # ---------------------------------------------------

        analytics = self.analytics.run(
            greeks_engine=self.greeks_engine,
            greeks_df=greeks_df,
            spot_price=spot,
        )

        # ---------------------------------------------------
        # Decision
        # ---------------------------------------------------

        decision = self.decision.build(
            analytics
        )

        # ---------------------------------------------------
        # Execute
        # ---------------------------------------------------

        if decision.valid:

            position = self.paper_broker.execute(
                decision
            )

            if position:

                print("Trade Executed")

        else:

            print("WAIT")

    # -------------------------------------------------------
    # Run
    # -------------------------------------------------------

    def run(self):

        self.initialize()

        while True:

            try:

                self.process_market()

            except Exception as ex:

                print(ex)

            print()

            time.sleep(
                self.runtime_config.refresh_interval
            )