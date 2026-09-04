from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace

from execution.execution_audit_store import ExecutionAuditRecord, SQLiteExecutionAuditStore
from execution.execution_recovery import recover_pending
from execution.recovery_runtime_gate import evaluate_recovery_runtime
from execution.reconciliation import ReconciliationStatus


def build_record(client_order_id: str, status: str) -> ExecutionAuditRecord:
    now = datetime.now()
    return ExecutionAuditRecord(
        client_order_id=client_order_id,
        symbol="NIFTY",
        option_type="CE",
        strike=25000,
        quantity=75,
        action="BUY",
        limit_price=120.0,
        strategy_name="TEST",
        source="test",
        broker_order_id="ORD-1",
        status=status,
        filled_quantity=0,
        average_fill_price=None,
        reason="",
        intent_created_at=now,
        result_timestamp=now,
    )


def test_pending_provider_state_is_recovery_blocking_until_reconciled(tmp_path):
    db_path = tmp_path / "execution_audit.sqlite"
    store = SQLiteExecutionAuditStore(db_path)
    store.append(build_record("provider-restart-1", "UNKNOWN"))

    pending = recover_pending(store)
    assert len(pending) == 1

    recovery = evaluate_recovery_runtime(
        SimpleNamespace(
            safe_to_continue=False,
            requires_reconciliation=True,
            requires_manual_resolution=False,
            reason="Persisted execution outcome is ambiguous; broker reconciliation is required before continuation.",
        ),
        reconciliation_report=None,
    )

    assert recovery.safe_to_continue is False
    assert recovery.requires_reconciliation is True
    store.close()


def test_pending_provider_state_can_continue_only_after_reconciliation_match(tmp_path):
    db_path = tmp_path / "execution_audit.sqlite"
    store = SQLiteExecutionAuditStore(db_path)
    store.append(build_record("provider-restart-2", "SUBMITTED"))
    pending = recover_pending(store)
    assert len(pending) == 1

    recovery = evaluate_recovery_runtime(
        SimpleNamespace(
            safe_to_continue=False,
            requires_reconciliation=True,
            requires_manual_resolution=False,
            reason="Persisted execution outcome is ambiguous; broker reconciliation is required before continuation.",
        ),
        reconciliation_report=SimpleNamespace(status=ReconciliationStatus.MATCH),
    )

    assert recovery.safe_to_continue is True
    assert recovery.requires_reconciliation is False
    store.close()
