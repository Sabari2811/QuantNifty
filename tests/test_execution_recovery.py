from datetime import datetime

from execution.execution_audit_store import ExecutionAuditRecord, InMemoryExecutionAuditStore
from execution.execution_recovery import evaluate_recovery, recover_pending


def record(status: str) -> ExecutionAuditRecord:
    now = datetime.now()
    return ExecutionAuditRecord(
        client_order_id="client-1",
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


def test_recover_pending_returns_only_ambiguous_records():
    store = InMemoryExecutionAuditStore()
    store.append(record("UNKNOWN"))
    pending = recover_pending(store)
    assert len(pending) == 1
    assert pending[0].status == "UNKNOWN"
