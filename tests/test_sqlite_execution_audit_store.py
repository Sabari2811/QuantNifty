from datetime import datetime

import pytest

from execution.execution_audit_store import ExecutionAuditRecord, SQLiteExecutionAuditStore
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


def test_sqlite_store_survives_reopen(tmp_path):
    path = tmp_path / "execution_audit.sqlite"
    record = ExecutionAuditRecord.from_result(make_result())

    with SQLiteExecutionAuditStore(path) as store:
        store.append(record)

    with SQLiteExecutionAuditStore(path) as reopened:
        assert reopened.get("client-1") == record
        assert reopened.records() == (record,)


def test_sqlite_store_is_idempotent_for_identical_record(tmp_path):
    path = tmp_path / "execution_audit.sqlite"
    record = ExecutionAuditRecord.from_result(make_result())

    with SQLiteExecutionAuditStore(path) as store:
        store.append(record)
        store.append(record)
        assert store.records() == (record,)


def test_sqlite_store_rejects_conflicting_record(tmp_path):
    path = tmp_path / "execution_audit.sqlite"
    record = ExecutionAuditRecord.from_result(make_result())
    conflicting = ExecutionAuditRecord.from_result(
        make_result(status=ExecutionStatus.REJECTED)
    )

    with SQLiteExecutionAuditStore(path) as store:
        store.append(record)
        with pytest.raises(ValueError, match="already exists"):
            store.append(conflicting)


def test_sqlite_store_loads_only_ambiguous_records(tmp_path):
    path = tmp_path / "execution_audit.sqlite"
    submitted = ExecutionAuditRecord.from_result(
        make_result(ExecutionStatus.SUBMITTED, "client-1")
    )
    unknown = ExecutionAuditRecord.from_result(
        make_result(ExecutionStatus.UNKNOWN, "client-2")
    )
    executed = ExecutionAuditRecord.from_result(
        make_result(ExecutionStatus.EXECUTED, "client-3")
    )

    with SQLiteExecutionAuditStore(path) as store:
        for record in (submitted, unknown, executed):
            store.append(record)
        assert {r.client_order_id for r in store.load_pending()} == {
            "client-1",
            "client-2",
        }
