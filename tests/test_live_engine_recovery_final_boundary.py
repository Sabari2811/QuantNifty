from __future__ import annotations

from types import SimpleNamespace

from execution.execution_audit_store import ExecutionAuditRecord, SQLiteExecutionAuditStore
from execution.execution_contract import ExecutionAction, ExecutionResult, ExecutionStatus, OrderIntent
from execution.execution_recovery import evaluate_recovery, recover_pending
from execution.recovery_runtime_gate import evaluate_recovery_runtime


def build_record(status: str, client_order_id: str = "final-boundary-1") -> ExecutionAuditRecord:
    intent = OrderIntent(
        symbol="NIFTY",
        option_type="CE",
        strike=25000,
        action=ExecutionAction.BUY,
        quantity=75,
        limit_price=120.0,
        client_order_id=client_order_id,
    )
    result = ExecutionResult(status=ExecutionStatus(status), intent=intent)
    return ExecutionAuditRecord.from_result(result)


def test_unknown_persisted_execution_cannot_resume_without_reconciliation():
    recovery = evaluate_recovery(build_record("UNKNOWN"))
    runtime = evaluate_recovery_runtime(recovery, reconciliation_report=None)

    assert runtime.safe_to_continue is False
    assert runtime.requires_reconciliation is True
    assert runtime.requires_manual_resolution is False


def test_unknown_persisted_execution_resumes_only_after_match():
    recovery = evaluate_recovery(build_record("UNKNOWN"))
    runtime = evaluate_recovery_runtime(
        recovery,
        reconciliation_report=SimpleNamespace(status="MATCH"),
    )

    assert runtime.safe_to_continue is True
    assert runtime.requires_reconciliation is False


def test_unknown_persisted_execution_stays_blocked_on_mismatch():
    recovery = evaluate_recovery(build_record("UNKNOWN"))
    runtime = evaluate_recovery_runtime(
        recovery,
        reconciliation_report=SimpleNamespace(status="MISMATCH"),
    )

    assert runtime.safe_to_continue is False
    assert runtime.requires_reconciliation is True
    assert runtime.requires_manual_resolution is True


def test_restart_store_returns_only_pending_ambiguous_records(tmp_path):
    db_path = tmp_path / "execution_audit.sqlite"
    store = SQLiteExecutionAuditStore(db_path)
    store.append(build_record("UNKNOWN", "pending-final"))
    store.append(build_record("EXECUTED", "terminal-final"))
    store.close()

    reopened = SQLiteExecutionAuditStore(db_path)
    pending = recover_pending(reopened)
    reopened.close()

    assert [record.client_order_id for record in pending] == ["pending-final"]
