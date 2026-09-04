from __future__ import annotations

from types import SimpleNamespace

from execution.execution_contract import ExecutionAction, ExecutionResult, ExecutionStatus, OrderIntent
from execution.execution_mode import ExecutionMode
from execution.live_execution_runtime_guard import LiveExecutionRuntimeGuard


class FakeAdapter:
    def __init__(self):
        self.calls = 0

    def execute(self, intent):
        self.calls += 1
        return ExecutionResult(
            status=ExecutionStatus.EXECUTED,
            intent=intent,
            broker_order_id="ORD-1",
            filled_quantity=intent.quantity,
            average_fill_price=intent.limit_price,
        )


def build_intent() -> OrderIntent:
    return OrderIntent(
        symbol="NIFTY",
        option_type="CE",
        strike=25000,
        action=ExecutionAction.BUY,
        quantity=75,
        limit_price=120.0,
        client_order_id="qn-live-boundary-1",
    )


def test_execution_mode_is_explicit():
    assert ExecutionMode.PAPER.value == "PAPER"
    assert ExecutionMode.LIVE.value == "LIVE"


def test_live_guard_is_not_implicitly_constructed_for_paper_mode():
    adapter = FakeAdapter()
    guard = LiveExecutionRuntimeGuard(adapter, SimpleNamespace(check=lambda: (True, "ok")))

    assert guard.adapter is adapter
    assert adapter.calls == 0


def test_live_guard_executes_only_when_explicitly_invoked():
    adapter = FakeAdapter()
    guard = LiveExecutionRuntimeGuard(adapter, SimpleNamespace(check=lambda: (True, "ok")))

    result = guard.execute(intent=build_intent())

    assert result.status is ExecutionStatus.EXECUTED
    assert adapter.calls == 1
