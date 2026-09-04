from __future__ import annotations

from types import SimpleNamespace

from execution.execution_contract import ExecutionAction, ExecutionResult, ExecutionStatus, OrderIntent
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


class FlexibleAdapter:
    def __init__(self):
        self.calls = []

    def execute(self, intent, decision=None):
        self.calls.append((intent, decision))
        return ExecutionResult(
            status=ExecutionStatus.EXECUTED,
            intent=intent,
            broker_order_id="ORD-1",
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
        client_order_id="qn-safety-regression-1",
    )
    return SimpleNamespace(
        decision=SimpleNamespace(trade=SimpleNamespace()),
        execution_intent=intent,
        intelligence=None,
        decision_intelligence_consistency=None,
    )


def test_pipeline_preserves_legacy_two_argument_adapter_contract():
    broker = FakePaperBroker()
    adapter = FlexibleAdapter()
    pipeline = TradeExecutionPipeline(broker, FakeRiskManager(), execution_adapter=adapter)

    ctx = build_ctx()
    pipeline.execute(ctx)

    assert len(adapter.calls) == 1
    assert adapter.calls[0][0] is ctx.execution_intent
    assert adapter.calls[0][1] is ctx.decision
    assert broker.calls == 0
    assert ctx.execution_result.status is ExecutionStatus.EXECUTED


def test_pipeline_passes_reconciliation_context_when_present():
    broker = FakePaperBroker()
    adapter = FlexibleAdapter()
    pipeline = TradeExecutionPipeline(broker, FakeRiskManager(), execution_adapter=adapter)

    ctx = build_ctx()
    reconciliation_result = SimpleNamespace(status=ExecutionStatus.SUBMITTED)
    reconciliation_report = SimpleNamespace(status="MATCH")
    ctx.reconciliation_result = reconciliation_result
    ctx.reconciliation_report = reconciliation_report

    pipeline.execute(ctx)

    assert len(adapter.calls) == 1
    assert adapter.calls[0][0] is ctx.execution_intent
    assert adapter.calls[0][1] is ctx.decision
    assert ctx.execution_result.status is ExecutionStatus.EXECUTED
