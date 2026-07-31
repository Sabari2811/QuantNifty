from providers.provider_manager import ProviderManager

from engine.instrument_manager import InstrumentManager
from engine.market_data_manager import MarketDataManager
from engine.strike_selector import StrikeSelector
from engine.option_chain_manager import OptionChainManager
from engine.live_greeks_engine import LiveGreeksEngine

from analytics.exposure_engine import ExposureEngine
from analytics.analytics_pipeline import AnalyticsPipeline


class MarketService:

    def __init__(self):

        # ======================================================
        # Provider
        # ======================================================

        self.provider = ProviderManager().get_provider()

        # ======================================================
        # Instrument Manager
        # ======================================================

        self.instrument = InstrumentManager()

        self.instrument.load_fno()

        self.instrument.load_index()

        # ======================================================
        # Market Manager
        # ======================================================

        self.market = MarketDataManager(
            self.provider
        )

        # ======================================================
        # Strike Selector
        # ======================================================

        self.selector = StrikeSelector(
            self.instrument
        )

        # ======================================================
        # Option Chain
        # ======================================================

        self.chain = OptionChainManager(

            self.provider,

            self.selector,

            self.instrument,

            self.market

        )

        # ======================================================
        # Greeks
        # ======================================================

        self.greeks = LiveGreeksEngine()

        # ======================================================
        # Exposure
        # ======================================================

        self.exposure = ExposureEngine()

        # ======================================================
        # Analytics
        # ======================================================

        self.pipeline = AnalyticsPipeline()

    # ======================================================
    # Dashboard Data
    # ======================================================

    def get_dashboard_data(

        self,

        symbol="NIFTY",

        levels=5

    ):

        # ------------------------------------------------------
        # Spot
        # ------------------------------------------------------

        spot = self.market.get_spot_price(symbol)

        # ------------------------------------------------------
        # Expiry
        # ------------------------------------------------------

        expiry = self.instrument.get_nearest_weekly_expiry(
            symbol
        )

        # ------------------------------------------------------
        # Option Chain
        # ------------------------------------------------------

        option_chain = self.chain.get_live_option_chain(

            symbol=symbol,

            spot_price=spot,

            levels=levels

        )

        # ------------------------------------------------------
        # Greeks
        # ------------------------------------------------------

        greeks_df = self.greeks.calculate_chain_greeks(

            option_chain,

            spot,

            expiry

        )

        # ------------------------------------------------------
        # Exposure
        # ------------------------------------------------------

        greeks_df = self.exposure.calculate(
            greeks_df
        )

        # ------------------------------------------------------
        # Analytics
        # ------------------------------------------------------

        analytics = self.pipeline.run(

            greeks_engine=self.greeks.greeks,

            greeks_df=greeks_df,

            spot_price=spot

        )

        # ------------------------------------------------------
        # Dashboard Response
        # ------------------------------------------------------

        return {

            "spot": spot,

            "expiry": expiry,

            "option_chain": option_chain,

            "greeks": greeks_df,

            "analytics": analytics

        }