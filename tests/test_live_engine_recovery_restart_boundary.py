from __future__ import annotations

from types import SimpleNamespace

from execution.execution_audit_store import ExecutionAuditRecord, InMemoryExecutionAuditStore
from execution.execution_recovery import evaluate_recovery
from execution.recovery_runtime_gate import evaluate_recovery_runtime
from execution.reconciliation import ReconciliationStatus


def build_record(status: str) -> ExecutionAuditRecord:
    from datetime import datetime

    return ExecutionAuditRecord(
        client_order_id="qn-restart-1",
        symbol="NIFTY",
        option_type="CE",
        strike=25000,
        quantity=75,
        action="BUY",
        limit_price=120.0,
        strategy_name="TEST",
        source="decision",
        broker_order_id="ORD-1",
        status=status,
        filled_quantity=75 if status == "EXECUTED" else 0,
        average_fill_price=120.0 if status == "EXECUTED" else None,
        reason="",
        intent_created_at=datetime.now(),
        result_timestamp=datetime.now(),
    )


def test_restart_recovery_blocks_ambiguous_persisted_order_without_reconciliation():
    store = InMemoryExecutionAuditStore()
    record = build_record("UNKNOWN")
    store.append(record)

    recovered = store.load_pending()
    assert recovered == (record,)

    recovery = evaluate_recovery(recovered[0])
    runtime = evaluate_recovery_runtime(recovery, reconciliation_report=None)

    assert runtime.safe_to_continue is False
    assert runtime.requires_reconciliation is True
    assert runtime.requires_manual_resolution is False


def test_restart_recovery_allows_ambiguous_order_only_after_match():
    store = InMemoryExecutionAuditStore()
    record = build_record("SUBMITTED")
    store.append(record)

    recovered = store.load_pending()
    recovery = evaluate_recovery(recovered[0])
    runtime = evaluate_recovery_runtime(
        recovery,
        reconciliation_report=SimpleNamespace(status=ReconciliationStatus.MATCH),
    )

    assert runtime.safe_to_continue is True
    assert runtime.requires_reconciliation is False
    assert runtime.requires_manual_resolution is False


def test_restart_recovery_requires_manual_resolution_on_mismatch():
    store = InMemoryExecutionAuditStore()
    record = build_record("UNKNOWN")
    store.append(record)

    recovered = store.load_pending()
    recovery = evaluate_recovery(recovered[0])
    runtime = evaluate_recovery_runtime(
        recovery,
        reconciliation_report=SimpleNamespace(status=ReconciliationStatus.MISMATCH),
    )

    assert runtime.safe_to_continue is False
    assert runtime.requires_reconciliation is True
    assert runtime.requires_manual_resolution is True


def test_terminal_executed_state_is_safe_to_resume_after_restart():
    store = InMemoryExecutionAuditStore()
    record = build_record("EXECUTED")
    store.append(record)

    recovered = store.get(record.client_order_id)
    recovery = evaluate_recovery(recovered)
    runtime = evaluate_recovery_runtime(recovery, reconciliation_report=None)

    assert runtime.safe_to_continue is True
    assert runtime.requires_reconciliation is False
    assert runtime.requires_manual_resolution is False
