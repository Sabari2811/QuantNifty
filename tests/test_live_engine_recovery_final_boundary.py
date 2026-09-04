from __future__ import annotations

from types import SimpleNamespace

from execution.execution_audit_store import ExecutionAuditRecord, SQLiteExecutionAuditStore
from execution.execution_contract import ExecutionAction, ExecutionResult, ExecutionStatus, OrderIntent
from execution.execution_recovery import evaluate_recovery, recover_pending
from execution.recovery_runtime_gate import evaluate_recovery_runtime
from execution.reconciliation import ReconciliationStatus


def build_record(status: str, client_order_id: str) -> ExecutionAuditRecord:
    intent = OrderIntent(
        symbol="NIFTY",
        option_type="CE",
        strike=25000,
        action=ExecutionAction.BUY,
        quantity=75,
        limit_price=120.0,
        client_order_id=client_order_id,
    )
    return ExecutionAuditRecord.from_result(
        ExecutionResult(status=ExecutionStatus(status), intent=intent)
    )


def test_persisted_ambiguous_state_requires_reconciliation(tmp_path):
    store = SQLiteExecutionAuditStore(tmp_path / "execution.sqlite")
    store.append(build_record("UNKNOWN", "final-unknown"))

    pending = recover_pending(store)
    recovery = evaluate_recovery(pending[0])
    runtime = evaluate_recovery_runtime(recovery, reconciliation_report=None)
    store.close()

    assert runtime.safe_to_continue is False
    assert runtime.requires_reconciliation is True
    assert runtime.requires_manual_resolution is False


def test_persisted_ambiguous_state_continues_only_after_match(tmp_path):
    store = SQLiteExecutionAuditStore(tmp_path / "execution.sqlite")
    store.append(build_record("SUBMITTED", "final-submitted"))

    pending = recover_pending(store)
    recovery = evaluate_recovery(pending[0])
    runtime = evaluate_recovery_runtime(
        recovery,
        reconciliation_report=SimpleNamespace(status=ReconciliationStatus.MATCH),
    )
    store.close()

    assert runtime.safe_to_continue is True
    assert runtime.requires_reconciliation is False
    assert runtime.requires_manual_resolution is False


def test_recovery_mismatch_requires_manual_resolution(tmp_path):
    store = SQLiteExecutionAuditStore(tmp_path / "execution.sqlite")
    store.append(build_record("UNKNOWN", "final-mismatch"))

    pending = recover_pending(store)
    recovery = evaluate_recovery(pending[0])
    runtime = evaluate_recovery_runtime(
        recovery,
        reconciliation_report=SimpleNamespace(status=ReconciliationStatus.MISMATCH),
    )
    store.close()

    assert runtime.safe_to_continue is False
    assert runtime.requires_reconciliation is True
    assert runtime.requires_manual_resolution is True
