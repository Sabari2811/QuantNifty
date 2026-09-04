from __future__ import annotations

from types import SimpleNamespace

from execution.execution_contract import ExecutionAction, ExecutionResult, ExecutionStatus, OrderIntent
from execution.execution_recovery import RecoveryDecision
from execution.recovery_runtime_gate import evaluate_recovery_runtime
from execution.reconciliation import ReconciliationStatus


class FakeProvider:
    def __init__(self):
        self.connect_calls = 0

    def connect(self):
        self.connect_calls += 1


class FakeStore:
    def __init__(self, records):
        self.records = tuple(records)
        self.closed = False

    def load_pending(self):
        return self.records

    def close(self):
        self.closed = True


def build_record(status: str) -> SimpleNamespace:
    intent = OrderIntent(
        symbol="NIFTY",
        option_type="CE",
        strike=25000,
        action=ExecutionAction.BUY,
        quantity=75,
        limit_price=120.0,
        client_order_id=f"qn-session-{status.lower()}",
    )
    result = ExecutionResult(status=ExecutionStatus(status), intent=intent)
    return SimpleNamespace(
        client_order_id=intent.client_order_id,
        status=status,
        result=result,
    )


def test_recovery_runtime_session_requires_reconciliation_for_pending_state():
    record = build_record("UNKNOWN")
    recovery = RecoveryDecision(
        safe_to_continue=False,
        requires_reconciliation=True,
        requires_manual_resolution=False,
        reason="Persisted execution outcome is ambiguous; broker reconciliation is required before continuation.",
    )

    decision = evaluate_recovery_runtime(recovery, reconciliation_report=None)

    assert record.status == "UNKNOWN"
    assert decision.safe_to_continue is False
    assert decision.requires_reconciliation is True
    assert decision.requires_manual_resolution is False


def test_recovery_runtime_session_allows_matched_pending_state():
    recovery = RecoveryDecision(
        safe_to_continue=False,
        requires_reconciliation=True,
        requires_manual_resolution=False,
        reason="Persisted execution outcome is ambiguous; broker reconciliation is required before continuation.",
    )
    report = SimpleNamespace(status=ReconciliationStatus.MATCH)

    decision = evaluate_recovery_runtime(recovery, reconciliation_report=report)

    assert decision.safe_to_continue is True
    assert decision.requires_reconciliation is False
    assert decision.requires_manual_resolution is False
