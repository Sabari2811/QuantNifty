from __future__ import annotations

from types import SimpleNamespace

from execution.execution_audit_store import ExecutionAuditRecord, SQLiteExecutionAuditStore
from execution.execution_recovery import evaluate_recovery, recover_pending


def build_record(status: str, client_order_id: str = "recovery-provider-1") -> ExecutionAuditRecord:
    from datetime import datetime

    return ExecutionAuditRecord(
        client_order_id=client_order_id,
        symbol="NIFTY",
        option_type="CE",
        strike=25000.0,
        quantity=75,
        action="BUY",
        limit_price=120.0,
        strategy_name="TEST",
        source="test",
        broker_order_id="ORD-1",
        status=status,
        filled_quantity=75 if status == "EXECUTED" else 0,
        average_fill_price=120.0 if status == "EXECUTED" else None,
        reason="",
        intent_created_at=datetime.now(),
        result_timestamp=datetime.now(),
    )


def test_recover_pending_uses_durable_store_interface(tmp_path):
    store = SQLiteExecutionAuditStore(tmp_path / "recovery.db")
    store.append(build_record("UNKNOWN"))
    store.append(build_record("EXECUTED", "recovery-provider-2"))

    pending = recover_pending(store)

    assert len(pending) == 1
    assert pending[0].client_order_id == "recovery-provider-1"
    store.close()


def test_evaluate_recovery_does_not_infer_broker_state():
    recovery = evaluate_recovery(build_record("SUBMITTED"))

    assert recovery.safe_to_continue is False
    assert recovery.requires_reconciliation is True
    assert recovery.requires_manual_resolution is False


def test_restart_runtime_requires_explicit_reconciliation_for_pending_state(tmp_path):
    store = SQLiteExecutionAuditStore(tmp_path / "restart.db")
    record = build_record("UNKNOWN")
    store.append(record)

    recovered = recover_pending(store)
    decision = evaluate_recovery(recovered[0])

    assert decision.requires_reconciliation is True
    assert decision.safe_to_continue is False
    store.close()
