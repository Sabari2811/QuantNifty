from __future__ import annotations

from datetime import datetime
from tempfile import TemporaryDirectory

from execution.execution_audit_store import ExecutionAuditRecord, SQLiteExecutionAuditStore
from execution.execution_recovery import recover_pending


def build_record(status: str, client_order_id: str = "qn-recovery-runtime-store-1"):
    now = datetime.now()
    return ExecutionAuditRecord(
        client_order_id=client_order_id,
        symbol="NIFTY",
        option_type="CE",
        strike=25000,
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
        intent_created_at=now,
        result_timestamp=now,
    )


def test_recover_pending_reads_durable_store_after_restart():
    with TemporaryDirectory() as tmp:
        path = f"{tmp}/execution.sqlite"
        with SQLiteExecutionAuditStore(path) as store:
            store.append(build_record("UNKNOWN"))

        reopened = SQLiteExecutionAuditStore(path)
        try:
            pending = recover_pending(reopened)
            assert len(pending) == 1
            assert pending[0].client_order_id == "qn-recovery-runtime-store-1"
            assert pending[0].status == "UNKNOWN"
        finally:
            reopened.close()


def test_recover_pending_excludes_terminal_execution_after_restart():
    with TemporaryDirectory() as tmp:
        path = f"{tmp}/execution.sqlite"
        with SQLiteExecutionAuditStore(path) as store:
            store.append(build_record("EXECUTED"))

        reopened = SQLiteExecutionAuditStore(path)
        try:
            assert recover_pending(reopened) == ()
        finally:
            reopened.close()
