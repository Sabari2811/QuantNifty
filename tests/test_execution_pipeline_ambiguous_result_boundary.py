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


class AmbiguousAdapter:
    def __init__(self):
        self.calls = 0

    def execute(self, intent, decision=None):
        self.calls += 1
        return ExecutionResult(
            status=ExecutionStatus.UNKNOWN,
            intent=intent,
            reason="broker outcome ambiguous",
        )


def build_ctx():
    intent = OrderIntent(
        symbol="NIFTY",
        option_type="CE",
        strike=25000,
        action=ExecutionAction.BUY,
        quantity=75,
        limit_price=120.0,
        client_order_id="qn-ambiguous-result-1",
    )
    return SimpleNamespace(
        decision=SimpleNamespace(trade=SimpleNamespace()),
        execution_intent=intent,
        intelligence=None,
        decision_intelligence_consistency=None,
    )


def test_pipeline_preserves_ambiguous_result_without_retry_or_paper_fallback():
    broker = FakePaperBroker()
    adapter = AmbiguousAdapter()
    pipeline = TradeExecutionPipeline(broker, FakeRiskManager(), execution_adapter=adapter)

    ctx = build_ctx()
    pipeline.execute(ctx)

    assert adapter.calls == 1
    assert broker.calls == 0
    assert ctx.execution_result.status is ExecutionStatus.UNKNOWN
    assert ctx.execution_lifecycle == "RECONCILE"
    assert ctx.trade_status == "REJECTED"
