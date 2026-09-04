from __future__ import annotations

from types import SimpleNamespace

from execution.execution_contract import ExecutionAction, ExecutionResult, ExecutionStatus, OrderIntent
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


class LegacyAdapter:
    def __init__(self):
        self.calls = []

    def execute(self, intent, decision=None):
        self.calls.append((intent, decision))
        return ExecutionResult(
            status=ExecutionStatus.EXECUTED,
            intent=intent,
            broker_order_id="ORD-LEGACY",
            filled_quantity=intent.quantity,
            average_fill_price=intent.limit_price,
        )


def build_ctx():
    intent = OrderIntent(
        symbol="NIFTY",
        option_type="CE",
        strike=25000,
        action=ExecutionAction.BUY,
        quantity=75,
        limit_price=120.0,
        client_order_id="qn-recon-fallback-1",
    )
    return SimpleNamespace(
        decision=SimpleNamespace(trade=SimpleNamespace()),
        execution_intent=intent,
        intelligence=None,
        decision_intelligence_consistency=None,
    )


def test_pipeline_preserves_legacy_adapter_when_reconciliation_context_is_present():
    broker = FakePaperBroker()
    adapter = LegacyAdapter()
    pipeline = TradeExecutionPipeline(broker, FakeRiskManager(), execution_adapter=adapter)

    ctx = build_ctx()
    ctx.reconciliation_result = SimpleNamespace(status=ExecutionStatus.SUBMITTED)
    ctx.reconciliation_report = SimpleNamespace(status=ReconciliationStatus.MATCH)

    pipeline.execute(ctx)

    assert adapter.calls == [(ctx.execution_intent, ctx.decision)]
    assert ctx.execution_result.status is ExecutionStatus.EXECUTED
    assert broker.calls == 0
