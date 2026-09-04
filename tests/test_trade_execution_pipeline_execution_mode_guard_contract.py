from __future__ import annotations

from types import SimpleNamespace

from execution.execution_contract import ExecutionAction, ExecutionResult, ExecutionStatus, OrderIntent
from execution.live_execution_runtime_guard import LiveExecutionRuntimeGuard


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


def build_intent():
    return OrderIntent(
        symbol="NIFTY",
        option_type="CE",
        strike=25000,
        action=ExecutionAction.BUY,
        quantity=75,
        limit_price=120.0,
        client_order_id="qn-exec-mode-guard-contract-1",
    )


def test_live_runtime_guard_uses_keyword_only_execution_boundary():
    adapter = FakeAdapter()
    guard = LiveExecutionRuntimeGuard(
        adapter,
        SimpleNamespace(check=lambda: (True, "ok")),
    )

    result = guard.execute(intent=build_intent())

    assert result.status is ExecutionStatus.EXECUTED
    assert adapter.calls == 1
