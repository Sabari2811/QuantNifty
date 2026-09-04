from datetime import datetime

import pytest

from execution.execution_audit_store import ExecutionAuditRecord, InMemoryExecutionAuditStore
from execution.execution_contract import ExecutionAction, ExecutionResult, ExecutionStatus, OrderIntent


def make_result(status=ExecutionStatus.EXECUTED, client_order_id="client-1"):
    created = datetime(2026, 9, 4, 10, 0, 0)
    intent = OrderIntent(
        symbol="NIFTY",
        option_type="CE",
        strike=24000,
        action=ExecutionAction.BUY,
        quantity=75,
        limit_price=100.0,
        strategy_name="TEST",
        client_order_id=client_order_id,
        created_at=created,
    )
    return ExecutionResult(
        status=status,
        intent=intent,
        broker_order_id="broker-1",
        filled_quantity=75 if status is ExecutionStatus.EXECUTED else 0,
        average_fill_price=100.0 if status is ExecutionStatus.EXECUTED else None,
        timestamp=created,
    )


def test_record_preserves_canonical_execution_fields():
    record = ExecutionAuditRecord.from_result(make_result())

    assert record.client_order_id == "client-1"
    assert record.broker_order_id == "broker-1"
    assert record.status == "EXECUTED"
    assert record.quantity == 75
    assert record.action == "BUY"


def test_record_requires_canonical_client_identity():
    with pytest.raises(ValueError, match="client_order_id"):
        ExecutionAuditRecord.from_result(make_result(client_order_id=""))


def test_store_is_idempotent_for_identical_record():
    store = InMemoryExecutionAuditStore()
    record = ExecutionAuditRecord.from_result(make_result())

    store.append(record)
    store.append(record)

    assert store.get("client-1") == record
    assert store.records() == (record,)


def test_store_rejects_conflicting_record_for_same_client_identity():
    store = InMemoryExecutionAuditStore()
    record = ExecutionAuditRecord.from_result(make_result())
    conflicting = ExecutionAuditRecord.from_result(
        make_result(status=ExecutionStatus.REJECTED)
    )

    store.append(record)
    with pytest.raises(ValueError, match="already exists"):
        store.append(conflicting)


def test_pending_records_are_explicitly_recoverable():
    store = InMemoryExecutionAuditStore()
    submitted = ExecutionAuditRecord.from_result(make_result(ExecutionStatus.SUBMITTED, "client-1"))
    unknown = ExecutionAuditRecord.from_result(make_result(ExecutionStatus.UNKNOWN, "client-2"))
    executed = ExecutionAuditRecord.from_result(make_result(ExecutionStatus.EXECUTED, "client-3"))

    for record in (submitted, unknown, executed):
        store.append(record)

    assert {record.client_order_id for record in store.load_pending()} == {"client-1", "client-2"}


def test_missing_record_returns_none():
    store = InMemoryExecutionAuditStore()
    assert store.get("missing") is None
