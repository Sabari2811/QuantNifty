from datetime import datetime

from execution.execution_audit_store import ExecutionAuditRecord, SQLiteExecutionAuditStore
from execution.execution_contract import ExecutionAction, ExecutionResult, ExecutionStatus, OrderIntent
from execution.idempotency import IdempotencyStatus, OrderIdempotencyGuard


def test_first_client_order_id_is_new_and_reserved():
    guard = OrderIdempotencyGuard()

    result = guard.check_and_reserve("client-1")

    assert result.status is IdempotencyStatus.NEW
    assert result.client_order_id == "client-1"
    assert guard.contains("client-1") is True


def test_repeated_client_order_id_is_duplicate():
    guard = OrderIdempotencyGuard()
    guard.check_and_reserve("client-1")

    result = guard.check_and_reserve("client-1")

    assert result.status is IdempotencyStatus.DUPLICATE
    assert result.reason == "Client order already reserved"


def test_empty_client_order_id_is_invalid_and_not_reserved():
    guard = OrderIdempotencyGuard()

    result = guard.check_and_reserve("   ")

    assert result.status is IdempotencyStatus.INVALID
    assert result.client_order_id == ""
    assert guard.contains("") is False


def test_distinct_client_order_ids_are_independently_reservable():
    guard = OrderIdempotencyGuard()

    first = guard.check_and_reserve("client-1")
    second = guard.check_and_reserve("client-2")

    assert first.status is IdempotencyStatus.NEW
    assert second.status is IdempotencyStatus.NEW


def test_persistent_audit_identity_is_duplicate_after_restart(tmp_path):
    path = tmp_path / "execution_audit.sqlite"
    created = datetime(2026, 9, 6, 10, 0, 0)
    intent = OrderIntent(
        symbol="NIFTY",
        option_type="CE",
        strike=24000,
        action=ExecutionAction.BUY,
        quantity=75,
        limit_price=100.0,
        strategy_name="TEST",
        client_order_id="restart-safe-1",
        created_at=created,
    )
    result = ExecutionResult(
        status=ExecutionStatus.UNKNOWN,
        intent=intent,
        reason="transport outcome unknown",
        timestamp=created,
    )

    with SQLiteExecutionAuditStore(path) as store:
        store.append(ExecutionAuditRecord.from_result(result))

    with SQLiteExecutionAuditStore(path) as reopened:
        guard = OrderIdempotencyGuard(reopened)
        decision = guard.check_and_reserve("restart-safe-1")

    assert decision.status is IdempotencyStatus.DUPLICATE
    assert "execution audit" in decision.reason
