from __future__ import annotations

from datetime import datetime

from execution.execution_audit_store import ExecutionAuditRecord, SQLiteExecutionAuditStore
from execution.execution_recovery import recover_pending


def build_record(client_order_id: str, status: str) -> ExecutionAuditRecord:
    now = datetime.now()
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
        filled_quantity=0,
        average_fill_price=None,
        reason="",
        intent_created_at=now,
        result_timestamp=now,
    )


def test_recover_pending_reads_ambiguous_records_from_sqlite(tmp_path):
    path = tmp_path / "recovery.sqlite"
    store = SQLiteExecutionAuditStore(path)
    try:
        store.append(build_record("pending-1", "UNKNOWN"))
        store.append(build_record("pending-2", "SUBMITTED"))
        store.append(build_record("done-1", "EXECUTED"))

        pending = recover_pending(store)

        assert [record.client_order_id for record in pending] == ["pending-1", "pending-2"]
        assert all(record.status in {"UNKNOWN", "SUBMITTED"} for record in pending)
    finally:
        store.close()
