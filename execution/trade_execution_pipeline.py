from __future__ import annotations

from analytics.intelligence.gate import IntelligenceGate
from execution.execution_contract import ExecutionStatus, ExecutionResult
from execution.execution_lifecycle import classify_execution_result
from execution.idempotency import IdempotencyStatus, OrderIdempotencyGuard
from execution.paper_execution_adapter import PaperExecutionAdapter


class TradeExecutionPipeline:
    """
    Handles the complete trade execution workflow.

    Responsibilities
    ----------------
    - Synchronize RuntimeContext
    - Intelligence eligibility gate
    - Decision/Intelligence consistency and actionability gate
    - Risk Validation
    - Canonical client-order idempotency gate
    - Canonical paper execution result propagation
    - Update RuntimeContext
    """

    def __init__(self, paper_broker, risk_manager, intelligence_gate=None, idempotency_guard=None, execution_adapter=None):
        self.paper_broker = paper_broker
        self.risk_manager = risk_manager
        self.intelligence_gate = intelligence_gate if intelligence_gate is not None else IntelligenceGate()
        self.idempotency_guard = idempotency_guard if idempotency_guard is not None else OrderIdempotencyGuard()
        self.execution_adapter = execution_adapter if execution_adapter is not None else PaperExecutionAdapter(paper_broker)

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
                print("\n" + "=" * 70)
                print("INTELLIGENCE GATE")
                print("=" * 70)
                print(intelligence_result.reason)
                return

            consistency = getattr(ctx, "decision_intelligence_consistency", None)
            if consistency is not None and not consistency.actionable:
                self._reject(ctx, getattr(ctx, "execution_intent", None), consistency.reason)
                semantic_status = getattr(consistency, "semantic_status", "CONFLICT")
                title = (
                    "DECISION / INTELLIGENCE DEFERRAL GATE"
                    if semantic_status == "DEFERRED"
                    else "DECISION / INTELLIGENCE CONSISTENCY GATE"
                )
                print("\n" + "=" * 70)
                print(title)
                print("=" * 70)
                print(consistency.reason)
                return

        try:
            ok, reason = self.risk_manager.validate(
                self.paper_broker,
                ctx.decision,
                context=ctx,
            )
        except TypeError:
            ok, reason = self.risk_manager.validate(self.paper_broker, ctx.decision)

        if not ok:
            self._reject(ctx, getattr(ctx, "execution_intent", None), reason)
            print("\n" + "=" * 70)
            print("RISK MANAGER")
            print("=" * 70)
            print(reason)
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
            result = self.execution_adapter.execute(intent, ctx.decision)
            ctx.execution_result = result
            ctx.execution_lifecycle = classify_execution_result(result).value
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
