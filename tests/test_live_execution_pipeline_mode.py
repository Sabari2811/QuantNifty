from __future__ import annotations

from types import SimpleNamespace

from execution.execution_contract import ExecutionAction, ExecutionResult, ExecutionStatus, OrderIntent
from execution.kill_switch import KillSwitch
from execution.live_execution_runtime_guard import LiveExecutionRuntimeGuard
from execution.reconciliation import ReconciliationStatus


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


def build_intent() -> OrderIntent:
    return OrderIntent(
        symbol="NIFTY",
        option_type="CE",
        strike=25000,
        action=ExecutionAction.BUY,
        quantity=75,
        limit_price=120.0,
        client_order_id="qn-runtime-mode-1",
    )


def test_live_runtime_guard_requires_reconciliation_for_ambiguous_result():
    adapter = FakeAdapter()
    guard = LiveExecutionRuntimeGuard(adapter, KillSwitch())

    result = guard.execute(
        intent=build_intent(),
        reconciliation_result=SimpleNamespace(status=ExecutionStatus.UNKNOWN),
        reconciliation_report=None,
    )

    assert result.status is ExecutionStatus.REJECTED
    assert "reconciliation report" in result.reason.lower()
    assert adapter.calls == 0


def test_live_runtime_guard_allows_reconciled_submission():
    adapter = FakeAdapter()
    guard = LiveExecutionRuntimeGuard(adapter, KillSwitch())

    result = guard.execute(
        intent=build_intent(),
        reconciliation_result=SimpleNamespace(status=ExecutionStatus.SUBMITTED),
        reconciliation_report=SimpleNamespace(status=ReconciliationStatus.MATCH),
    )

    assert result.status is ExecutionStatus.SUBMITTED
    assert adapter.calls == 1
