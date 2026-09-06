from __future__ import annotations

from analytics.intelligence.gate import IntelligenceGate
from execution.execution_audit_store import ExecutionAuditRecord, InMemoryExecutionAuditStore, SQLiteExecutionAuditStore
from execution.execution_contract import ExecutionStatus, ExecutionResult
from execution.execution_lifecycle import classify_execution_result
from execution.idempotency import IdempotencyStatus, OrderIdempotencyGuard
from execution.paper_execution_adapter import PaperExecutionAdapter


class TradeExecutionPipeline:
    """Canonical trade execution workflow and audit boundary."""

    def __init__(self, paper_broker, risk_manager, intelligence_gate=None, idempotency_guard=None, execution_adapter=None, audit_store=None, audit_db_path=None):
        self.paper_broker = paper_broker
        self.risk_manager = risk_manager
        self.intelligence_gate = intelligence_gate if intelligence_gate is not None else IntelligenceGate()
        self.idempotency_guard = idempotency_guard if idempotency_guard is not None else OrderIdempotencyGuard()
        self.execution_adapter = execution_adapter if execution_adapter is not None else PaperExecutionAdapter(paper_broker)
        if audit_store is not None and audit_db_path is not None:
            raise ValueError("Provide either audit_store or audit_db_path, not both")
        self.audit_store = audit_store if audit_store is not None else (
            SQLiteExecutionAuditStore(audit_db_path)
            if audit_db_path is not None
            else InMemoryExecutionAuditStore()
        )

    def sync_context(self, ctx):
        broker = self.paper_broker
        ctx.portfolio = broker.portfolio_engine.portfolio
        ctx.position = getattr(broker, "position", None)
        ctx.last_trade = getattr(broker, "last_trade", None)
        ctx.journal = getattr(broker, "journal", None)
        ctx.statistics = ctx.journal.summary() if ctx.journal is not None else {}
        ctx.risk_state = self.risk_manager.state

    def _client_order_id(self, ctx):
        intent = getattr(ctx, "execution_intent", None)
        return str(getattr(intent, "client_order_id", "")).strip()

    def _persist_result(self, result):
        if result is not None and result.intent.client_order_id:
            self.audit_store.append(ExecutionAuditRecord.from_result(result))

    def _reject(self, ctx, intent, reason):
        ctx.trade_status = "BLOCKED"
        ctx.trade_block_reason = reason
        if intent is not None:
            ctx.execution_result = ExecutionResult(
                status=ExecutionStatus.REJECTED,
                intent=intent,
                reason=reason,
            )
            ctx.execution_lifecycle = classify_execution_result(ctx.execution_result).value
            self._persist_result(ctx.execution_result)

    def _execute_adapter(self, intent, decision, reconciliation_result, reconciliation_report):
        if reconciliation_result is not None:
            try:
                return self.execution_adapter.execute(
                    intent=intent,
                    reconciliation_result=reconciliation_result,
                    reconciliation_report=reconciliation_report,
                )
            except TypeError as exc:
                if "reconciliation_result" not in str(exc) and "reconciliation_report" not in str(exc):
                    raise
                return self.execution_adapter.execute(intent, decision)

        try:
            return self.execution_adapter.execute(intent, decision)
        except TypeError:
            return self.execution_adapter.execute(intent=intent)

    def execute(self, ctx):
        self.sync_context(ctx)
        ctx.trade_status = ""
        ctx.trade_block_reason = ""
        ctx.execution_result = None
        ctx.execution_lifecycle = ""

        if ctx.decision is None:
            return
        trade = getattr(ctx.decision, "trade", None)
        if trade is None:
            return

        if ctx.intelligence is not None:
            intelligence_result = self.intelligence_gate.evaluate(ctx.intelligence)
            if not intelligence_result.allowed:
                self._reject(ctx, getattr(ctx, "execution_intent", None), intelligence_result.reason)
                return

            consistency = getattr(ctx, "decision_intelligence_consistency", None)
            if consistency is not None and not consistency.actionable:
                self._reject(ctx, getattr(ctx, "execution_intent", None), consistency.reason)
                return

        try:
            ok, reason = self.risk_manager.validate(self.paper_broker, ctx.decision, context=ctx)
        except TypeError:
            ok, reason = self.risk_manager.validate(self.paper_broker, ctx.decision)

        if not ok:
            self._reject(ctx, getattr(ctx, "execution_intent", None), reason)
            return

        intent = getattr(ctx, "execution_intent", None)
        client_order_id = self._client_order_id(ctx)
        if intent is not None and client_order_id:
            idempotency = self.idempotency_guard.check_and_reserve(client_order_id)
            if idempotency.status is IdempotencyStatus.INVALID:
                self._reject(ctx, intent, idempotency.reason)
                return
            if idempotency.status is IdempotencyStatus.DUPLICATE:
                self._reject(ctx, intent, "Client order already submitted.")
                return

        if intent is not None:
            reconciliation_result = getattr(ctx, "reconciliation_result", None)
            reconciliation_report = getattr(ctx, "reconciliation_report", None)
            result = self._execute_adapter(
                intent,
                ctx.decision,
                reconciliation_result,
                reconciliation_report,
            )
            ctx.execution_result = result
            ctx.execution_lifecycle = classify_execution_result(result).value
            self._persist_result(result)
            if result.status is ExecutionStatus.EXECUTED:
                ctx.trade_status = "EXECUTED"
                ctx.position = getattr(self.paper_broker, "position", None)
            else:
                ctx.trade_status = "REJECTED"
                ctx.trade_block_reason = result.reason or "Paper broker rejected execution"
        else:
            position = self.paper_broker.execute(ctx.decision)
            if position is not None:
                ctx.trade_status = "EXECUTED"
                ctx.position = position
            else:
                ctx.trade_status = "REJECTED"
                ctx.trade_block_reason = "Broker rejected trade execution."

        self.sync_context(ctx)


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
from analytics.intelligence.decision_consistency import reconcile_decision_intelligence

from execution.order_intent_factory import build_order_intent
from execution.trade_execution_pipeline import TradeExecutionPipeline
from execution.execution_lifecycle import classify_execution_result
from execution.runtime_audit_config import build_runtime_audit_store
from execution.position_runtime_config import build_position_state_store
from execution.position_runtime_service import PositionRuntimeService
from execution.position_recovery_runtime import recover_open_positions as recover_runtime_positions

from recording.recording_manager import RecordingManager

from ui.console_dashboard import ConsoleDashboard

from runtime.runtime_mode import RuntimeMode
from models.market_context import MarketContext
from simulation.replay_equivalence import (
    compare_replay_analytics,
    compare_replay_outputs,
)


class LiveEngine:

    def __init__(self, provider=None, intelligence_service=None, paper_broker=None, trade_pipeline=None, audit_store_path=None, position_state_path=None):
        self.ctx = RuntimeContext()
        self._previous_greeks_df = None
        self.provider = provider
        self.intelligence_service = intelligence_service
        self.paper_broker = paper_broker
        self.trade_pipeline = trade_pipeline
        self.audit_store_path = audit_store_path
        self.position_state_path = position_state_path
        self._runtime_audit_store = None
        self._position_state_store = None
        self.position_runtime_service = None
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
        if self.position_state_path is not None:
            self._position_state_store = build_position_state_store(self.position_state_path)
            self.position_runtime_service = PositionRuntimeService(self._position_state_store)
        if self.trade_pipeline is None:
            self.risk_manager = RiskManager()
            if self.audit_store_path is not None:
                self._runtime_audit_store = build_runtime_audit_store(self.audit_store_path)
            self.trade_pipeline = TradeExecutionPipeline(
                paper_broker=self.paper_broker,
                risk_manager=self.risk_manager,
                audit_store=self._runtime_audit_store,
            )
        else:
            self.risk_manager = self.trade_pipeline.risk_manager
        self.recording_manager = RecordingManager()
        self.dashboard = ConsoleDashboard()
        self.ctx.runtime_status = "READY"
        logger.info("Initialization Complete")

    def _recover_position_runtime_state(self):
        service = getattr(self, "position_runtime_service", None)
        if service is None:
            from execution.position_recovery_runtime import PositionRecoveryRuntimeDecision
            decision = PositionRecoveryRuntimeDecision(
                positions=(),
                safe_to_continue=False,
                reason="Position state store is unavailable.",
            )
        else:
            decision = recover_runtime_positions(service.store)
        self.ctx.position_recovery = decision
        return decision

    def _persist_position_runtime_state(self):
        service = getattr(self, "position_runtime_service", None)
        if service is None:
            return

        broker = self.paper_broker
        for position in getattr(broker.portfolio, "open_positions", ()):
            service.persist_paper_position(position)

        last_trade = getattr(broker, "last_trade", None)
        if last_trade is not None and getattr(last_trade, "closed", False):
            lifecycle = service.evaluate_paper_position(last_trade, manual_close=True)
            service.persist_after_lifecycle(last_trade, lifecycle)

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

    @staticmethod
    def _option_chain_ready_for_analytics(ctx):
        """Allow analytics only when the canonical option chain is complete and valid."""
        provenance = getattr(ctx, "data_provenance", None)
        option = getattr(provenance, "option_chain", None) if provenance else None
        if option is None:
            return False, "option_chain_provenance_unavailable"
        if option.coverage_status != "COMPLETE":
            return False, f"option_chain_coverage:{option.coverage_status}"
        if option.integrity_status == "INVALID":
            return False, "option_chain_integrity:INVALID"
        return True, ""

    def _run_analytics(self):
        replay_recompute = self._is_replay_recompute()
        computed_analytics = self.pipeline.run(
            greeks_engine=self.greeks.greeks,
            greeks_df=self.ctx.greeks_df,
            spot_price=self.ctx.spot,
            candles=self.ctx.candles,
            previous_greeks_df=getattr(self, "_previous_greeks_df", None),
        )

        computed_context = computed_analytics.get("context")
        if computed_context is None:
            raise RuntimeError("AnalyticsPipeline returned no canonical MarketContext")

        computed_greeks_df = getattr(computed_context, "greeks", None)
        if hasattr(computed_greeks_df, "copy"):
            self.ctx.greeks_df = computed_greeks_df.copy(deep=True)

        if replay_recompute:
            expected_analytics = getattr(self.ctx, "replay_expected_analytics", None)
            if expected_analytics:
                self.ctx.replay_computed_analytics = computed_analytics
                self.ctx.replay_computed_market_context = computed_context
                self.ctx.replay_analytics_equivalence = compare_replay_analytics(
                    expected_analytics,
                    computed_context,
                )
                self.ctx.market_context = MarketContext.from_analytics(
                    expected_analytics,
                    spot=self.ctx.spot,
                    greeks=self.ctx.greeks_df,
                )
                self.ctx.analytics = expected_analytics
            else:
                self.ctx.replay_computed_market_context = computed_context
                self.ctx.replay_analytics_equivalence = None
                self.ctx.market_context = computed_context
                self.ctx.analytics = computed_analytics
        else:
            self.ctx.market_context = computed_context
            self.ctx.replay_computed_market_context = None
            self.ctx.replay_analytics_equivalence = None
            self.ctx.analytics = computed_analytics

        greeks_for_snapshot = self.ctx.greeks_df
        if not hasattr(greeks_for_snapshot, "copy"):
            greeks_for_snapshot = computed_analytics.get("greeks")
        self.ctx.snapshot = MarketSnapshot().save(
            greeks_df=greeks_for_snapshot,
            spot=self.ctx.spot,
            analytics=self.ctx.analytics,
        )
        self.ctx.snapshot.market_context = self.ctx.market_context
        regime = self.market_regime.analyze(self.ctx.snapshot)
        self.ctx.snapshot.regime = regime
        self.ctx.regime = regime
        self.ctx.decision = self.decision_engine.build(self.ctx.snapshot)

        if replay_recompute:
            expected_decision = getattr(self.ctx, "replay_expected_decision", None)
            if isinstance(expected_decision, dict):
                canonical_trade = expected_decision.get("trade", {}) or {}
                canonical_strike = canonical_trade.get("strike")
                if canonical_strike is not None:
                    self.ctx.decision.trade.strike = canonical_strike

        self.ctx.explanation = self.explanation_engine.build(
            decision=self.ctx.decision,
            regime=self.ctx.regime,
            snapshot=self.ctx.snapshot,
        )

        if self.intelligence_service is not None:
            self.ctx.intelligence = self.intelligence_service.analyze(self.ctx)
            self.ctx.decision_intelligence_consistency = reconcile_decision_intelligence(
                self.ctx.decision,
                self.ctx.intelligence,
            )
        else:
            self.ctx.decision_intelligence_consistency = None

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

        self.ctx.execution_intent = build_order_intent(self.ctx.decision)

        self.trade_pipeline.execute(self.ctx)
        if self.ctx.execution_result is not None:
            self.ctx.execution_lifecycle = classify_execution_result(self.ctx.execution_result).value
        self._persist_position_runtime_state()

    def run_cycle(self):
        self.ctx.runtime_status = "RUNNING"
        self.ctx.cycle_no += 1
        self.ctx.timestamp = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
        try:
            self.market_pipeline.run(self.ctx)

            chain_ready, block_reason = self._option_chain_ready_for_analytics(self.ctx)
            if not chain_ready:
                self.ctx.runtime_status = "DEGRADED"
                self.ctx.trade_status = "BLOCKED"
                self.ctx.trade_block_reason = block_reason
                logger.warning(
                    "LIVE ENGINE DEGRADED | analytics/trading blocked | reason=%s",
                    block_reason,
                )
                self.trade_pipeline.sync_context(self.ctx)
                if not self._is_replay():
                    self.recording_manager.record(self.ctx)
                return self.ctx

            closed_before = len(self.paper_broker.portfolio.closed_positions)
            self.paper_broker.update_positions(self.ctx.option_chain)
            closed_after = len(self.paper_broker.portfolio.closed_positions)
            if closed_after > closed_before:
                position = self.paper_broker.last_trade
                if position is not None:
                    self.risk_manager.on_trade_closed(position)
            self._persist_position_runtime_state()
            self.trade_pipeline.sync_context(self.ctx)
            if self._is_replay_fast():
                pass
            else:
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
            if self.ctx.runtime_status not in {"ERROR", "DEGRADED"}:
                self.ctx.runtime_status = "IDLE"

    def build_context(self):
        return self.run_cycle()

    def run(self):
        logger.info("LIVE ENGINE STARTED")
        ctx = self.run_cycle()
        self.dashboard.show(ctx)
        return ctx
