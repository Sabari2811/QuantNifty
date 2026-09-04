from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace

from execution.execution_audit_store import ExecutionAuditRecord, InMemoryExecutionAuditStore
from execution.execution_recovery import recover_pending


def build_record(status: str, client_order_id: str = "qn-restart-1") -> ExecutionAuditRecord:
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
        source="decision",
        broker_order_id="ORD-1",
        status=status,
        filled_quantity=0,
        average_fill_price=None,
        reason="",
        intent_created_at=now,
        result_timestamp=now,
    )


def test_restart_recovery_reads_only_pending_ambiguous_records():
    store = InMemoryExecutionAuditStore()
    store.append(build_record("UNKNOWN", "qn-restart-unknown"))
    store.append(build_record("SUBMITTED", "qn-restart-submitted"))
    store.append(build_record("EXECUTED", "qn-restart-executed"))
    store.append(build_record("REJECTED", "qn-restart-rejected"))

    pending = recover_pending(store)

    assert [record.client_order_id for record in pending] == [
        "qn-restart-unknown",
        "qn-restart-submitted",
    ]


def test_restart_recovery_does_not_infer_broker_state():
    store = InMemoryExecutionAuditStore()
    store.append(build_record("UNKNOWN"))

    pending = recover_pending(store)

    assert len(pending) == 1
    assert pending[0].status == "UNKNOWN"
    assert pending[0].broker_order_id == "ORD-1"
