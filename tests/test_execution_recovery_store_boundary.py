from __future__ import annotations

from datetime import datetime
from tempfile import TemporaryDirectory

from execution.execution_audit_store import ExecutionAuditRecord, SQLiteExecutionAuditStore
from execution.execution_recovery import recover_pending


def build_record(status: str, client_order_id: str) -> ExecutionAuditRecord:
    return ExecutionAuditRecord(
        client_order_id=client_order_id,
        symbol="NIFTY",
        option_type="CE",
        strike=25000,
        quantity=75,
        action="BUY",
        limit_price=120.0,
        strategy_name="test",
        source="decision",
        broker_order_id="ORD-1",
        status=status,
        filled_quantity=0,
        average_fill_price=None,
        reason="",
        intent_created_at=datetime.now(),
        result_timestamp=datetime.now(),
    )


def test_recover_pending_reads_durable_ambiguous_records():
    with TemporaryDirectory() as directory:
        store = SQLiteExecutionAuditStore(f"{directory}/execution.db")
        store.append(build_record("UNKNOWN", "pending-1"))
        store.append(build_record("SUBMITTED", "pending-2"))
        store.append(build_record("EXECUTED", "done-1"))
        store.append(build_record("REJECTED", "done-2"))

        pending = recover_pending(store)

        assert [record.client_order_id for record in pending] == ["pending-1", "pending-2"]
        assert {record.status for record in pending} == {"UNKNOWN", "SUBMITTED"}

        store.close()
