from __future__ import annotations

from types import SimpleNamespace

from execution.execution_contract import ExecutionAction, ExecutionResult, ExecutionStatus, OrderIntent
from execution.live_execution_runtime_guard import LiveExecutionRuntimeGuard
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
        client_order_id="qn-exec-mode-wiring-1",
    )
    decision = SimpleNamespace(trade=SimpleNamespace())
    return SimpleNamespace(
        decision=decision,
        execution_intent=intent,
        intelligence=None,
        decision_intelligence_consistency=None,
    )


def test_default_pipeline_does_not_use_live_runtime_guard():
    broker = FakePaperBroker()
    pipeline = TradeExecutionPipeline(broker, FakeRiskManager())

    assert not isinstance(pipeline.execution_adapter, LiveExecutionRuntimeGuard)


def test_live_runtime_guard_is_explicitly_injectable_without_changing_pipeline_contract():
    broker = FakePaperBroker()
    adapter = FakeAdapter()
    guard = LiveExecutionRuntimeGuard(adapter, SimpleNamespace(check=lambda: (True, "ok")))
    pipeline = TradeExecutionPipeline(
        broker,
        FakeRiskManager(),
        execution_adapter=guard,
    )

    ctx = build_ctx()
    pipeline.execute(ctx)

    assert adapter.calls == 1
    assert broker.calls == 0
    assert ctx.execution_result.status is ExecutionStatus.EXECUTED
