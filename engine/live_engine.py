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
from simulation.replay_equivalence import compare_replay_outputs


class LiveEngine:

    def __init__(self, provider=None, intelligence_service=None, paper_broker=None, trade_pipeline=None):
        self.ctx = RuntimeContext()
        self._previous_greeks_df = None
        self.provider = provider
        self.intelligence_service = intelligence_service
        self.paper_broker = paper_broker
        self.trade_pipeline = trade_pipeline
        self._initialize()

    def _initialize(self):
        logger.info("INITIALIZING QUANTNIFTY")
        if self.provider is None:
            self.provider = INDMoneyProvider()
        self.provider.connect()
        self.instrument = InstrumentManager()
        self.market = MarketDataManager(self.provider)
        self.selector = StrikeSelector(self.instrument)
        self.chain_manager = OptionChainManager(self.provider, self.selector, self.instrument, self.market)
        self.greeks = LiveGreeksEngine()
        self.candle_manager = CandleManager()
        self.market_pipeline = MarketDataPipeline(provider=self.provider, instrument=self.instrument, market=self.market, chain_manager=self.chain_manager, candle_manager=self.candle_manager)
        self.pipeline = AnalyticsPipeline()
        self.market_regime = MarketRegimeEngine()
        self.decision_engine = DecisionEngine()
        self.explanation_engine = ExplanationEngine()
        if self.paper_broker is None:
            self.paper_broker = PaperBroker()
        if self.trade_pipeline is None:
            self.risk_manager = RiskManager()
            self.trade_pipeline = TradeExecutionPipeline(paper_broker=self.paper_broker, risk_manager=self.risk_manager)
        else:
            self.risk_manager = self.trade_pipeline.risk_manager
        self.recording_manager = RecordingManager()
        self.dashboard = ConsoleDashboard()
        self.ctx.runtime_status = "READY"
        logger.info("Initialization Complete")

    def _calculate_greeks(self):
        self.ctx.greeks_df = self.greeks.calculate_chain_greeks(self.ctx.option_chain, self.ctx.spot, self.ctx.expiry)
        logger.info("GREEKS DATAFRAME | columns=%s", self.ctx.greeks_df.columns.tolist())
        logger.debug("GREEKS DATAFRAME | head=\n%s", self.ctx.greeks_df.head().to_string())

    def _is_replay(self):
        return isinstance(getattr(self, "provider", None), SimulationProvider)

    def _is_replay_fast(self):
        return self._is_replay() and self.provider.runtime_mode == RuntimeMode.REPLAY_FAST

    def _is_replay_recompute(self):
        return self._is_replay() and self.provider.runtime_mode == RuntimeMode.REPLAY_RECOMPUTE

    def _run_analytics(self):
        replay_recompute = self._is_replay_recompute()
        computed_analytics = self.pipeline.run(
            greeks_engine=self.greeks.greeks,
            greeks_df=self.ctx.greeks_df,
            spot_price=self.ctx.spot,
            candles=self.ctx.candles,
            previous_greeks_df=getattr(self, "_previous_greeks_df", None),
        )

        if replay_recompute:
            expected_analytics = getattr(self.ctx, "replay_expected_analytics", None)
            if expected_analytics:
                self.ctx.replay_computed_analytics = computed_analytics
                self.ctx.analytics = expected_analytics
            else:
                self.ctx.analytics = computed_analytics
        else:
            self.ctx.analytics = computed_analytics

        greeks_for_snapshot = self.ctx.greeks_df
        if not hasattr(greeks_for_snapshot, "copy"):
            greeks_for_snapshot = computed_analytics.get("greeks")
        self.ctx.snapshot = MarketSnapshot().save(
            greeks_df=greeks_for_snapshot,
            spot=self.ctx.spot,
            analytics=self.ctx.analytics,
        )
        regime = self.market_regime.analyze(self.ctx.snapshot)
        self.ctx.snapshot.regime = regime
        self.ctx.regime = regime

        # Replay recompute must reconstruct the exact decision from the
        # canonical recorded decision inputs, but the execution plan should
        # not be allowed to mutate the canonical comparison object. We build
        # the decision normally, then compare before the optional execution
        # gate can alter runtime status.
        self.ctx.decision = self.decision_engine.build(self.ctx.snapshot)
        self.ctx.explanation = self.explanation_engine.build(
            decision=self.ctx.decision,
            regime=self.ctx.regime,
            snapshot=self.ctx.snapshot,
        )

        if self.intelligence_service is not None:
            self.ctx.intelligence = self.intelligence_service.analyze(self.ctx)

        if replay_recompute:
            expected_decision = getattr(self.ctx, "replay_expected_decision", None)
            expected_intelligence = getattr(self.ctx, "replay_expected_intelligence", None)
            actual_intelligence = getattr(self.ctx, "intelligence", None)
            if expected_decision is not None and expected_intelligence:
                self.ctx.replay_equivalence = compare_replay_outputs(
                    expected_decision,
                    self.ctx.decision,
                    expected_intelligence,
                    actual_intelligence,
                )
            else:
                self.ctx.replay_equivalence = None

        self.trade_pipeline.execute(self.ctx)

    def run_cycle(self):
        self.ctx.runtime_status = "RUNNING"
        self.ctx.cycle_no += 1
        self.ctx.timestamp = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
        try:
            self.market_pipeline.run(self.ctx)
            closed_before = len(self.paper_broker.portfolio.closed_positions)
            self.paper_broker.update_positions(self.ctx.option_chain)
            closed_after = len(self.paper_broker.portfolio.closed_positions)
            if closed_after > closed_before:
                position = self.paper_broker.last_trade
                if position is not None:
                    self.risk_manager.on_trade_closed(position)
            self.trade_pipeline.sync_context(self.ctx)
            if self._is_replay_fast():
                pass
            else:
                # Replay recompute consumes recorded canonical Greeks. Live
                # cycles continue to calculate Greeks from the live chain.
                if self._is_replay_recompute():
                    self.ctx.greeks_df = self.ctx.greeks_df.copy(deep=True)
                else:
                    self._calculate_greeks()
                self._run_analytics()
                self._previous_greeks_df = self.ctx.greeks_df.copy(deep=True)
            if not self._is_replay():
                self.recording_manager.record(self.ctx)
            return self.ctx
        except Exception:
            logger.exception("LIVE ENGINE ERROR")
            self.ctx.runtime_status = "ERROR"
            raise
        finally:
            if self.ctx.runtime_status != "ERROR":
                self.ctx.runtime_status = "IDLE"

    def build_context(self):
        return self.run_cycle()

    def run(self):
        logger.info("LIVE ENGINE STARTED")
        ctx = self.run_cycle()
        self.dashboard.show(ctx)
        return ctx
