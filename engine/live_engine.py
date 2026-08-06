from datetime import datetime
from core.runtime_context import RuntimeContext
from decision.explanation_engine import ExplanationEngine

from providers.indmoney_provider import INDMoneyProvider
from paper_trading.broker import PaperBroker

from engine.instrument_manager import InstrumentManager
from engine.market_data_manager import MarketDataManager
from engine.strike_selector import StrikeSelector
from engine.option_chain_manager import OptionChainManager
from decision.market_regime_engine import MarketRegimeEngine
from engine.live_greeks_engine import LiveGreeksEngine
from engine.candle_manager import CandleManager
from engine.market_data_pipeline import MarketDataPipeline
from risk.risk_manager import RiskManager

from analytics.analytics_pipeline import AnalyticsPipeline
from analytics.market_snapshot.market_snapshot import MarketSnapshot

from decision.decision_engine import DecisionEngine


from ui.console_dashboard import ConsoleDashboard
from execution.trade_execution_pipeline import TradeExecutionPipeline
from recording.recording_manager import RecordingManager
from providers.simulation_provider import SimulationProvider
from runtime.runtime_mode import RuntimeMode


class LiveEngine:

    def __init__(self, provider=None):

        self.ctx = RuntimeContext()

        self.provider = provider

        self._initialize()

    # ==========================================================
    # INITIALIZATION
    # ==========================================================

    def _initialize(self):

        print()
        print("=" * 70)
        print("INITIALIZING QUANTNIFTY")
        print("=" * 70)

        if self.provider is None:
            self.provider = INDMoneyProvider()

        self.provider.connect()

        self.instrument = InstrumentManager()

        self.market = MarketDataManager(
            self.provider
        )

        self.selector = StrikeSelector(
            self.instrument
        )

        self.chain_manager = OptionChainManager(
            self.provider,
            self.selector,
            self.instrument,
            self.market
        )

        self.greeks = LiveGreeksEngine()

        self.candle_manager = CandleManager()

        self.market_pipeline = MarketDataPipeline(

            provider=self.provider,

            instrument=self.instrument,

            market=self.market,

            chain_manager=self.chain_manager,

            candle_manager=self.candle_manager

        )

        self.pipeline = AnalyticsPipeline()

        self.market_regime = MarketRegimeEngine()

        # ------------------------------------------------------
        # Decision Engine
        # ------------------------------------------------------

        self.decision_engine = DecisionEngine()

        # ------------------------------------------------------
        # Explanation Engine
        # ------------------------------------------------------

        self.explanation_engine = ExplanationEngine()        

        # ------------------------------------------------------
        # Paper Trading
        # ------------------------------------------------------
        self.paper_broker = PaperBroker()

        self.risk_manager = RiskManager()

        self.trade_pipeline = TradeExecutionPipeline(

            paper_broker=self.paper_broker,

            risk_manager=self.risk_manager

        )

        self.recording_manager = RecordingManager()

        # ------------------------------------------------------
        # Console Dashboard
        # ------------------------------------------------------

        self.dashboard = ConsoleDashboard()

        self.ctx.runtime_status = "READY"

        print()
        print("Initialization Complete")


    # ==========================================================
    # GREEKS
    # ==========================================================

    def _calculate_greeks(self):

        self.ctx.greeks_df = self.greeks.calculate_chain_greeks(
            self.ctx.option_chain,
            self.ctx.spot,
            self.ctx.expiry
        )

        print()
        print("=" * 70)
        print("GREEKS DATAFRAME")
        print("=" * 70)

        print(self.ctx.greeks_df.columns.tolist())

        print()

        print(self.ctx.greeks_df.head())

    # ==========================================================
    # Runtime Helpers
    # ==========================================================

    def _is_replay(self):

        return isinstance(
            self.provider,
            SimulationProvider
        )


    def _is_replay_fast(self):

        return (

            self._is_replay()

            and

            self.provider.runtime_mode
            == RuntimeMode.REPLAY_FAST

        )


    def _is_replay_recompute(self):

        return (

            self._is_replay()

            and

            self.provider.runtime_mode
            == RuntimeMode.REPLAY_RECOMPUTE

        )


    # ==========================================================
    # ANALYTICS
    # ==========================================================

    def _run_analytics(self):

        self.ctx.analytics = self.pipeline.run(
            greeks_engine=self.greeks.greeks,
            greeks_df=self.ctx.greeks_df,
            spot_price=self.ctx.spot,
            candles=self.ctx.candles
        )

        # ------------------------------------------------------
        # Build Market Snapshot
        # ------------------------------------------------------

        self.ctx.snapshot = MarketSnapshot().save(
            greeks_df=self.ctx.analytics["greeks"],
            spot=self.ctx.spot,
            analytics=self.ctx.analytics
        )

        # ------------------------------------------------------
        # Market Regime
        # ------------------------------------------------------

        regime = self.market_regime.analyze(
            self.ctx.snapshot
        )

        self.ctx.snapshot.regime = regime
        self.ctx.regime = regime

        # ------------------------------------------------------
        # Build Institutional Decision
        # ------------------------------------------------------

        self.ctx.decision = self.decision_engine.build(
            self.ctx.snapshot
        )

        # ------------------------------------------------------
        # Market Explanation
        # ------------------------------------------------------

        self.ctx.explanation = self.explanation_engine.build(

            decision=self.ctx.decision,

            regime=self.ctx.regime,

            snapshot=self.ctx.snapshot

        )

        # ------------------------------------------------------
        # Execute Paper Trade
        # ------------------------------------------------------

        self.trade_pipeline.execute(self.ctx)

    # ==========================================================
    # ONE MARKET CYCLE
    # ==========================================================

    def run_cycle(self):
        """
        Executes one complete live market cycle.
        Can be called by Streamlit or Scheduler.
        """

        self.ctx.runtime_status = "RUNNING"

        self.ctx.cycle_no += 1

        self.ctx.timestamp = datetime.now().strftime(
            "%d-%b-%Y %H:%M:%S"
        )

        try:

            # --------------------------------------------------
            # Market Data
            # --------------------------------------------------

            self.market_pipeline.run(self.ctx)

            # --------------------------------------------------
            # Update Existing Paper Trades
            # --------------------------------------------------

            closed_before = len(
                    self.paper_broker.portfolio.closed_positions
                )

            self.paper_broker.update_positions(
                    self.ctx.option_chain
                )

            closed_after = len(
                    self.paper_broker.portfolio.closed_positions
                )

            if closed_after > closed_before:

                    position = self.paper_broker.last_trade

                    if position is not None:

                        self.risk_manager.on_trade_closed(
                            position
                        )

            self.trade_pipeline.sync_context(self.ctx)

            # --------------------------------------------------
            # Analytics
            # --------------------------------------------------

            if self._is_replay_fast():

                #
                # Snapshot already contains analytics.
                #
                pass

            else:

                self._calculate_greeks()

                self._run_analytics()

            # --------------------------------------------------
            # Snapshot Recording
            # --------------------------------------------------

            if not self._is_replay():

                self.recording_manager.record(self.ctx)

                return self.ctx

        except Exception as e:

            print()
            print("=" * 70)
            print("LIVE ENGINE ERROR")
            print("=" * 70)
            print(e)

            self.ctx.runtime_status = "ERROR"

            raise

        finally:

            if self.ctx.runtime_status != "ERROR":
                self.ctx.runtime_status = "IDLE"

    # ==========================================================
    # BUILD CONTEXT
    # ==========================================================

    def build_context(self):
        """
        Backward compatible wrapper.
        """

        return self.run_cycle()

    # ==========================================================
    # CONSOLE MODE
    # ==========================================================

    def run(self):

        print()
        print("=" * 70)
        print("LIVE ENGINE STARTED")
        print("=" * 70)

        ctx = self.run_cycle()

        self.dashboard.show(ctx)

        return ctx