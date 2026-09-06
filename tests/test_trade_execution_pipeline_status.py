from types import SimpleNamespace

import pytest

from execution.execution_contract import ExecutionResult, ExecutionStatus, OrderIntent, ExecutionAction
from execution.execution_lifecycle import ExecutionLifecycleAction
from execution.trade_execution_pipeline import TradeExecutionPipeline


class _Broker:
    def __init__(self):
        self.portfolio_engine = SimpleNamespace(portfolio={})
        self.position = None
        self.last_trade = None
        self.journal = None


class _RiskManager:
    state = "READY"

    def validate(self, broker, decision, context=None):
        return True, ""


class _Adapter:
    def __init__(self, result):
        self.result = result

    def execute(self, intent, decision=None, **kwargs):
        return self.result


def _context(status):
    intent = OrderIntent(
        symbol="NIFTY",
        option_type="CE",
        strike=24500,
        action=ExecutionAction.BUY,
        quantity=50,
        limit_price=100.0,
        client_order_id=f"test-{status.value.lower()}",
    )
    result = ExecutionResult(
        status=status,
        intent=intent,
        reason="broker outcome unresolved" if status is ExecutionStatus.UNKNOWN else "order accepted",
    )
    ctx = SimpleNamespace(
        decision=SimpleNamespace(trade=object()),
        intelligence=None,
        execution_intent=intent,
        reconciliation_result=None,
        reconciliation_report=None,
    )
    return ctx, result


@pytest.mark.parametrize(
    ("status", "expected_trade_status", "expected_lifecycle"),
    [
        (ExecutionStatus.UNKNOWN, "UNKNOWN", ExecutionLifecycleAction.RECONCILE.value),
        (ExecutionStatus.SUBMITTED, "SUBMITTED", ExecutionLifecycleAction.RECONCILE.value),
        (ExecutionStatus.REJECTED, "REJECTED", ExecutionLifecycleAction.DO_NOT_RETRY.value),
        (ExecutionStatus.FAILED, "FAILED", ExecutionLifecycleAction.DO_NOT_RETRY.value),
    ],
)
def test_pipeline_preserves_canonical_execution_status(status, expected_trade_status, expected_lifecycle):
    broker = _Broker()
    ctx, result = _context(status)
    pipeline = TradeExecutionPipeline(
        broker,
        _RiskManager(),
        execution_adapter=_Adapter(result),
    )

    pipeline.execute(ctx)

    assert ctx.execution_result is result
    assert ctx.trade_status == expected_trade_status
    assert ctx.execution_lifecycle == expected_lifecycle
    if status in {ExecutionStatus.UNKNOWN, ExecutionStatus.SUBMITTED}:
        assert ctx.trade_block_reason == ""
    else:
        assert ctx.trade_block_reason
