from datetime import datetime

from core.runtime_context import RuntimeContext
from core.logger import logger

from decision.explanation_engine import ExplanationEngine

from providers.indmoney_provider import INDMoneyProvider
from providers.simulation_provider import SimulationProvider

from paper_trading.broker import PaperBroker

from engine.instrument_manager import InstrumentManager
from engine.market_data_manager import MarketDataManager
from engine.strike_selector import StrikeSelector
from engine.option_chain_manager import OptionChainManager
from engine.live_greeks_engine import LiveGreeksEngine
from engine.candle_manager import CandleManager
from engine.market_data_pipeline import MarketDataPipeline

from decision.market_regime_engine import MarketRegimeEngine
from decision.decision_engine import DecisionEngine

from risk.risk_manager import RiskManager

from analytics.analytics_pipeline import AnalyticsPipeline
from analytics.market_snapshot.market_snapshot import MarketSnapshot

from execution.trade_execution_pipeline import TradeExecutionPipeline

from recording.recording_manager import RecordingManager

from ui.console_dashboard import ConsoleDashboard

from runtime.runtime_mode import RuntimeMode


class LiveEngine:

    def __init__(
        self,
        provider=None,
        intelligence_service=None,
        paper_broker=None,
        trade_pipeline=None,
    ):

        self.ctx = RuntimeContext()

        # Previous market snapshot used for delta-based OI flow.
        self._previous_greeks_df = None

        self.provider = provider

        #
        # C6 Intelligence Service
        #
        # Created by CompositionRoot and injected here.
        #

        self.intelligence_service = intelligence_service

        #
        # Paper Broker
        #
        # Prefer the CompositionRoot-owned broker.
        # Keep fallback for backward compatibility with
        # direct LiveEngine() construction.
        #

        self.paper_broker = paper_broker

        #
        # Trade Execution Pipeline
        #
        # Prefer the CompositionRoot-owned pipeline.
        # Keep fallback for backward compatibility with
        # direct LiveEngine() construction.
        #

        self.trade_pipeline = trade_pipeline

        self._initialize()

    # ==========================================================
    # INITIALIZATION
    # ==========================================================

    def _initialize(self):

        logger.info("INITIALIZING QUANTNIFTY")

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
        # Paper Trading / Execution
        # ------------------------------------------------------

        if self.paper_broker is None:

            self.paper_broker = PaperBroker()

        #
        # CompositionRoot owns the complete TradeExecutionPipeline.
        #
        # For direct LiveEngine() construction, preserve the
        # previous behavior by constructing the legacy dependencies.
        #

        if self.trade_pipeline is None:

            self.risk_manager = RiskManager()

            self.trade_pipeline = TradeExecutionPipeline(
                paper_broker=self.paper_broker,
                risk_manager=self.risk_manager
            )

        else:

            #
            # The injected pipeline is authoritative.
            #

            self.risk_manager = (
                self.trade_pipeline.risk_manager
            )

        self.recording_manager = RecordingManager()

        # ------------------------------------------------------
        # Console Dashboard
        # ------------------------------------------------------

        self.dashboard = ConsoleDashboard()

        self.ctx.runtime_status = "READY"

        logger.info("Initialization Complete")

    # ==========================================================
    # GREEKS
    # ==========================================================

    def _calculate_greeks(self):

        self.ctx.greeks_df = self.greeks.calculate_chain_greeks(
            self.ctx.option_chain,
            self.ctx.spot,
            self.ctx.expiry
        )

        logger.info(
            "GREEKS DATAFRAME | columns=%s",
            self.ctx.greeks_df.columns.tolist(),
        )

        logger.debug(
            "GREEKS DATAFRAME | head=\n%s",
            self.ctx.greeks_df.head().to_string(),
        )

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
            candles=self.ctx.candles,
            previous_greeks_df=getattr(
                self,
                "_previous_greeks_df",
                None,
            ),
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
        # Intelligence Layer
        # ------------------------------------------------------

        if self.intelligence_service is not None:

            self.ctx.intelligence = (
                self.intelligence_service.analyze(
                    self.ctx
                )
            )

        # ------------------------------------------------------
        # Execute Paper Trade
        # ------------------------------------------------------

        self.trade_pipeline.execute(
            self.ctx
        )

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

            self.market_pipeline.run(
                self.ctx
            )

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

            self.trade_pipeline.sync_context(
                self.ctx
            )

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

                # Preserve the successfully processed snapshot
                # for delta-based OI analysis on the next cycle.
                self._previous_greeks_df = self.ctx.greeks_df.copy(
                    deep=True
                )

            # --------------------------------------------------
            # Snapshot Recording
            # --------------------------------------------------

            if not self._is_replay():

                self.recording_manager.record(
                    self.ctx
                )

            return self.ctx

        except Exception as e:

            logger.exception(
                "LIVE ENGINE ERROR"
            )

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

        logger.info("LIVE ENGINE STARTED")

        ctx = self.run_cycle()

        self.dashboard.show(
            ctx
        )

        return ctx