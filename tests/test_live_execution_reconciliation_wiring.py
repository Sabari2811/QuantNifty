from __future__ import annotations

from types import SimpleNamespace

from execution.execution_contract import ExecutionAction, ExecutionResult, ExecutionStatus, OrderIntent
from execution.live_execution_runtime_guard import LiveExecutionRuntimeGuard
from execution.reconciliation import ReconciliationStatus
from execution.trade_execution_pipeline import TradeExecutionPipeline


class FakeRiskManager:
    def __init__(self):
        self.state = SimpleNamespace()

    def validate(self, broker, decision, context=None):
        return True, ""


class FakePaperBroker:
    def __init__(self):
        self.portfolio_engine = SimpleNamespace(portfolio=SimpleNamespace())
        self.position = None
        self.last_trade = None
        self.journal = None
        self.calls = 0

    def execute(self, decision):
        self.calls += 1
        return SimpleNamespace()


class FakeLiveAdapter:
    def __init__(self):
        self.calls = 0

    def execute(self, intent, decision=None):
        self.calls += 1
        return ExecutionResult(
            status=ExecutionStatus.SUBMITTED,
            intent=intent,
            broker_order_id="ORD-1",
        )


class FakeGuard:
    def __init__(self, adapter):
        self.adapter = adapter
        self.calls = []

    def execute(self, *, intent, reconciliation_result=None, reconciliation_report=None):
        self.calls.append((intent, reconciliation_result, reconciliation_report))
        if reconciliation_result is not None and reconciliation_report is None:
            return ExecutionResult(
                status=ExecutionStatus.REJECTED,
                intent=intent,
                reason="Ambiguous execution requires a reconciliation report.",
            )
        return self.adapter.execute(intent)


def build_ctx():
    intent = OrderIntent(
        symbol="NIFTY",
        option_type="CE",
        strike=25000,
        action=ExecutionAction.BUY,
        quantity=75,
        limit_price=120.0,
        client_order_id="qn-live-recon-wiring-1",
    )
    decision = SimpleNamespace(trade=SimpleNamespace())
    return SimpleNamespace(
        decision=decision,
        execution_intent=intent,
        intelligence=None,
        decision_intelligence_consistency=None,
    )


def test_live_guard_boundary_receives_runtime_reconciliation_context():
    broker = FakePaperBroker()
    adapter = FakeLiveAdapter()
    guard = FakeGuard(adapter)
    pipeline = TradeExecutionPipeline(broker, FakeRiskManager(), execution_adapter=guard)

    ctx = build_ctx()
    reconciliation_result = SimpleNamespace(status=ExecutionStatus.SUBMITTED)
    reconciliation_report = SimpleNamespace(status=ReconciliationStatus.MATCH)
    ctx.reconciliation_result = reconciliation_result
    ctx.reconciliation_report = reconciliation_report

    pipeline.execute(ctx)

    assert adapter.calls == 1
    assert broker.calls == 0
    assert len(guard.calls) == 1
    assert guard.calls[0][1] is reconciliation_result
    assert guard.calls[0][2] is reconciliation_report


def test_live_guard_boundary_rejects_ambiguous_runtime_without_report():
    broker = FakePaperBroker()
    adapter = FakeLiveAdapter()
    guard = FakeGuard(adapter)
    pipeline = TradeExecutionPipeline(broker, FakeRiskManager(), execution_adapter=guard)

    ctx = build_ctx()
    reconciliation_result = SimpleNamespace(status=ExecutionStatus.UNKNOWN)
    ctx.reconciliation_result = reconciliation_result
    ctx.reconciliation_report = None

    pipeline.execute(ctx)

    assert adapter.calls == 0
    assert broker.calls == 0
    assert ctx.execution_result.status is ExecutionStatus.REJECTED
    assert "reconciliation report" in ctx.execution_result.reason.lower()
