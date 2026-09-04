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


class FakeLiveAdapter:
    def __init__(self):
        self.calls = []

    def execute(self, intent):
        self.calls.append(intent)
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
        client_order_id="qn-live-guard-adapter-1",
    )
    return SimpleNamespace(
        decision=SimpleNamespace(trade=SimpleNamespace()),
        execution_intent=intent,
        intelligence=None,
        decision_intelligence_consistency=None,
    )


def test_pipeline_executes_live_runtime_guard_using_canonical_keyword_boundary():
    broker = FakePaperBroker()
    live_adapter = FakeLiveAdapter()
    guard = LiveExecutionRuntimeGuard(
        live_adapter,
        SimpleNamespace(check=lambda: (True, "ok")),
    )
    pipeline = TradeExecutionPipeline(
        broker,
        FakeRiskManager(),
        execution_adapter=guard,
    )

    ctx = build_ctx()
    pipeline.execute(ctx)

    assert len(live_adapter.calls) == 1
    assert live_adapter.calls[0] is ctx.execution_intent
    assert broker.calls == 0
    assert ctx.execution_result.status is ExecutionStatus.SUBMITTED
