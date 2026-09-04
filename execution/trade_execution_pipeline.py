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
            if reconciliation_result is not None:
                try:
                    result = self.execution_adapter.execute(
                        intent=intent,
                        reconciliation_result=reconciliation_result,
                        reconciliation_report=reconciliation_report,
                    )
                except TypeError as exc:
                    if "reconciliation_result" not in str(exc) and "reconciliation_report" not in str(exc):
                        raise
                    result = self.execution_adapter.execute(intent, ctx.decision)
            else:
                try:
                    result = self.execution_adapter.execute(intent, ctx.decision)
                except TypeError:
                    result = self.execution_adapter.execute(intent=intent)
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
