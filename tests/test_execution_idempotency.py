from datetime import datetime

from execution.execution_audit_store import ExecutionAuditRecord, SQLiteExecutionAuditStore
from execution.idempotency import IdempotencyStatus, OrderIdempotencyGuard


def _record(client_order_id: str) -> ExecutionAuditRecord:
    now = datetime.now()
    return ExecutionAuditRecord(
        client_order_id=client_order_id,
        symbol="NIFTY",
        option_type="CE",
        strike=25000,
        quantity=75,
        action="BUY",
        limit_price=100.0,
        strategy_name="test",
        source="test",
        broker_order_id="BROKER-1",
        status="EXECUTED",
        filled_quantity=75,
        average_fill_price=99.5,
        reason="",
        intent_created_at=now,
        result_timestamp=now,
    )


def test_idempotency_uses_durable_audit_across_guard_restart(tmp_path):
    db = tmp_path / "execution_audit.sqlite"
    with SQLiteExecutionAuditStore(db) as store:
        store.append(_record("CLIENT-001"))

    with SQLiteExecutionAuditStore(db) as reopened:
        guard = OrderIdempotencyGuard(reopened)
        decision = guard.check_and_reserve("CLIENT-001")

    assert decision.status is IdempotencyStatus.DUPLICATE
    assert "audit" in decision.reason.lower()


def test_new_client_order_is_reserved_once_within_process(tmp_path):
    with SQLiteExecutionAuditStore(tmp_path / "execution_audit.sqlite") as store:
        guard = OrderIdempotencyGuard(store)
        first = guard.check_and_reserve("CLIENT-002")
        second = guard.check_and_reserve("CLIENT-002")

    assert first.status is IdempotencyStatus.NEW
    assert second.status is IdempotencyStatus.DUPLICATE
