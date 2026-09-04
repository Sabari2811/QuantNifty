from types import SimpleNamespace

from execution.execution_contract import ExecutionAction, ExecutionResult, ExecutionStatus, OrderIntent
from execution.kill_switch import KillSwitch
from execution.live_execution_runtime_guard import LiveExecutionRuntimeGuard


class FakeAdapter:
    def __init__(self):
        self.calls = 0

    def execute(self, intent):
        self.calls += 1
        return ExecutionResult(
            status=ExecutionStatus.SUBMITTED,
            intent=intent,
            broker_order_id="ORD-1",
        )


def intent():
    return OrderIntent(
        symbol="NIFTY",
        option_type="CE",
        strike=25000,
        action=ExecutionAction.BUY,
        quantity=75,
        limit_price=120.0,
        client_order_id="qn-runtime-1",
    )


def test_active_kill_switch_blocks_live_adapter():
    adapter = FakeAdapter()
    switch = KillSwitch()
    switch.activate("manual stop")
    guard = LiveExecutionRuntimeGuard(adapter, switch)

    result = guard.execute(intent=intent())

    assert result.status is ExecutionStatus.REJECTED
    assert result.reason == "Kill switch active: manual stop"
    assert adapter.calls == 0


def test_inactive_kill_switch_allows_live_adapter():
    adapter = FakeAdapter()
    guard = LiveExecutionRuntimeGuard(adapter, KillSwitch())

    result = guard.execute(intent=intent())

    assert result.status is ExecutionStatus.SUBMITTED
    assert result.broker_order_id == "ORD-1"
    assert adapter.calls == 1


def test_ambiguous_reconciliation_blocks_live_execution():
    adapter = FakeAdapter()
    guard = LiveExecutionRuntimeGuard(adapter, KillSwitch())
    reconciliation_result = SimpleNamespace(status=SimpleNamespace(value="UNKNOWN"))

    result = guard.execute(
        intent=intent(),
        reconciliation_result=reconciliation_result,
        reconciliation_report=None,
    )

    assert result.status is ExecutionStatus.REJECTED
    assert "reconciliation report" in result.reason.lower()
    assert adapter.calls == 0


def test_matched_reconciliation_allows_live_execution():
    adapter = FakeAdapter()
    guard = LiveExecutionRuntimeGuard(adapter, KillSwitch())
    reconciliation_result = SimpleNamespace(status=SimpleNamespace(value="SUBMITTED"))
    reconciliation_report = SimpleNamespace(status=SimpleNamespace(value="MATCH"))

    result = guard.execute(
        intent=intent(),
        reconciliation_result=reconciliation_result,
        reconciliation_report=reconciliation_report,
    )

    assert result.status is ExecutionStatus.SUBMITTED
    assert adapter.calls == 1
