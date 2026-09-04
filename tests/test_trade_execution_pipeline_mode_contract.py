from __future__ import annotations

from types import SimpleNamespace

from execution.execution_contract import ExecutionAction, ExecutionResult, ExecutionStatus, OrderIntent
from execution.execution_lifecycle import classify_execution_result
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


class FakeAdapter:
    def __init__(self):
        self.calls = 0

    def execute(self, intent, decision=None):
        self.calls += 1
        return ExecutionResult(
            status=ExecutionStatus.SUBMITTED,
            intent=intent,
            broker_order_id="ORD-1",
        )


def build_ctx():
    intent = OrderIntent(
        symbol="NIFTY",
        option_type="CE",
        strike=25000,
        action=ExecutionAction.BUY,
        quantity=75,
        limit_price=120.0,
        client_order_id="qn-mode-contract-1",
    )
    decision = SimpleNamespace(
        trade=SimpleNamespace(),
        execution_intent=intent,
    )
    return SimpleNamespace(
        decision=decision,
        execution_intent=intent,
        intelligence=None,
        decision_intelligence_consistency=None,
    )


def test_pipeline_default_is_paper_adapter():
    broker = FakePaperBroker()
    pipeline = TradeExecutionPipeline(broker, FakeRiskManager())

    assert pipeline.execution_adapter.__class__.__name__ == "PaperExecutionAdapter"
    assert pipeline.paper_broker is broker


def test_pipeline_accepts_explicit_adapter_without_changing_default_broker_role():
    broker = FakePaperBroker()
    adapter = FakeAdapter()
    pipeline = TradeExecutionPipeline(
        broker,
        FakeRiskManager(),
        execution_adapter=adapter,
    )

    ctx = build_ctx()
    pipeline.execute(ctx)

    assert adapter.calls == 1
    assert broker.calls == 0
    assert ctx.execution_result.status is ExecutionStatus.SUBMITTED
    assert ctx.execution_lifecycle == classify_execution_result(ctx.execution_result).value
