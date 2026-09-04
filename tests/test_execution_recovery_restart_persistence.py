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
        strike=25000,
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


def test_pending_recovery_survives_store_reopen(tmp_path):
    db_path = tmp_path / "execution_audit.sqlite"
    first = SQLiteExecutionAuditStore(db_path)
    first.append(build_record("restart-1", "UNKNOWN"))
    first.close()

    second = SQLiteExecutionAuditStore(db_path)
    pending = recover_pending(second)
    second.close()

    assert len(pending) == 1
    assert pending[0].client_order_id == "restart-1"
    assert pending[0].status == "UNKNOWN"


def test_terminal_execution_is_not_pending_after_store_reopen(tmp_path):
    db_path = tmp_path / "execution_audit.sqlite"
    first = SQLiteExecutionAuditStore(db_path)
    first.append(build_record("restart-2", "EXECUTED"))
    first.close()

    second = SQLiteExecutionAuditStore(db_path)
    pending = recover_pending(second)
    second.close()

    assert pending == ()
