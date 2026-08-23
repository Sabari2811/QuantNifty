from datetime import datetime, timedelta

from providers.simulation_provider import SimulationProvider


class MarketDataPipeline:
    """
    Responsible for preparing RuntimeContext with market data.

    Supports both:

        • Live Provider
        • Simulation Provider
    """

    def __init__(
        self,
        provider,
        instrument,
        market,
        chain_manager,
        candle_manager
    ):

        self.provider = provider
        self.instrument = instrument
        self.market = market
        self.chain_manager = chain_manager
        self.candle_manager = candle_manager

    # ==========================================================
    # LIVE PIPELINE
    # ==========================================================

    def _run_live(self, ctx):

        self._fetch_spot(ctx)

        self._fetch_option_chain(ctx)

        self._fetch_historical_candles(ctx)

    # ==========================================================
    # REPLAY PIPELINE
    # ==========================================================

    def _run_replay(self, ctx):

        snapshot = self.provider.next_cycle()

        ctx.timestamp = snapshot.timestamp

        ctx.cycle_no = snapshot.cycle_no

        ctx.symbol = snapshot.symbol

        ctx.spot = snapshot.spot

        ctx.option_chain = snapshot.option_chain.copy()

        ctx.greeks_df = snapshot.greeks.copy()

        ctx.analytics = snapshot.analytics

        ctx.decision = snapshot.decision

        ctx.explanation = snapshot.explanation

        #
        # Historical candles are already part of analytics
        # during replay.
        #
        ctx.candles = None

    # ==========================================================
    # LIVE
    # ==========================================================

    def _fetch_spot(self, ctx):

        ctx.spot = self.market.get_spot_price(
            ctx.symbol
        )

    def _fetch_option_chain(self, ctx):

        ctx.expiry = self.instrument.get_nearest_weekly_expiry(
            ctx.symbol
        )

        ctx.option_chain = self.chain_manager.get_live_option_chain(
            ctx.symbol,
            ctx.spot,
            5
        )

    def _fetch_historical_candles(self, ctx):

        security_id = self.instrument.get_index_security_id(
            ctx.symbol
        )

        scrip_code = self.instrument.get_scrip_code(
            "NIDX",
            security_id
        )

        end = datetime.now()

        start = end - timedelta(days=5)

        candles = self.provider.get_historical_data(

            scrip_code=scrip_code,

            interval="5minute",

            start_time=int(start.timestamp() * 1000),

            end_time=int(end.timestamp() * 1000)

        )

        ctx.candles = self.candle_manager.to_dataframe(
            candles
        )

    # ==========================================================
    # PUBLIC
    # ==========================================================

    def run(self, ctx):

        if isinstance(
            self.provider,
            SimulationProvider
        ):

            self._run_replay(ctx)

        else:

            self._run_live(ctx)
