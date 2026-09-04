from datetime import datetime

import pytest

from execution.execution_audit_store import ExecutionAuditRecord, InMemoryExecutionAuditStore, SQLiteExecutionAuditStore
from execution.execution_recovery import evaluate_recovery, recover_pending


def record(status: str, client_order_id: str = "client-1") -> ExecutionAuditRecord:
    now = datetime.now()
    return ExecutionAuditRecord(
        client_order_id=client_order_id,
        symbol="NIFTY",
        option_type="CE",
        strike=24000,
        quantity=75,
        action="BUY",
        limit_price=100.0,
        strategy_name="TEST",
        source="decision",
        broker_order_id="broker-1",
        status=status,
        filled_quantity=75 if status == "EXECUTED" else 0,
        average_fill_price=100.0 if status == "EXECUTED" else None,
        reason="",
        intent_created_at=now,
        result_timestamp=now,
    )


def test_unknown_requires_reconciliation():
    decision = evaluate_recovery(record("UNKNOWN"))
    assert decision.safe_to_continue is False
    assert decision.requires_reconciliation is True
    assert decision.requires_manual_resolution is False


def test_submitted_requires_reconciliation():
    decision = evaluate_recovery(record("SUBMITTED"))
    assert decision.safe_to_continue is False
    assert decision.requires_reconciliation is True


def test_executed_terminal_state_can_resume():
    decision = evaluate_recovery(record("EXECUTED"))
    assert decision.safe_to_continue is True
    assert decision.requires_reconciliation is False


def test_rejected_never_resumes_automatically():
    decision = evaluate_recovery(record("REJECTED"))
    assert decision.safe_to_continue is False
    assert decision.requires_manual_resolution is True


def test_failed_never_resumes_automatically():
    decision = evaluate_recovery(record("FAILED"))
    assert decision.safe_to_continue is False
    assert decision.requires_manual_resolution is True


def test_unknown_status_is_fail_closed():
    decision = evaluate_recovery(record("SOMETHING_ELSE"))
    assert decision.safe_to_continue is False
    assert decision.requires_manual_resolution is True


def test_recover_pending_returns_only_ambiguous_records_in_memory():
    store = InMemoryExecutionAuditStore()
    store.append(record("UNKNOWN"))
    pending = recover_pending(store)
    assert len(pending) == 1
    assert pending[0].status == "UNKNOWN"


def test_recover_pending_reads_durable_sqlite_records(tmp_path):
    db_path = tmp_path / "execution_audit.db"
    with SQLiteExecutionAuditStore(db_path) as store:
        store.append(record("UNKNOWN", "client-1"))
        store.append(record("EXECUTED", "client-2"))
        pending = recover_pending(store)

    assert [item.client_order_id for item in pending] == ["client-1"]
    assert pending[0].status == "UNKNOWN"
