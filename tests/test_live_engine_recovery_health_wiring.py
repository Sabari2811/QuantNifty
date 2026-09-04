from __future__ import annotations

from types import SimpleNamespace

from execution.execution_audit_store import ExecutionAuditRecord, SQLiteExecutionAuditStore
from execution.execution_contract import ExecutionAction, ExecutionResult, ExecutionStatus, OrderIntent
from execution.execution_recovery import evaluate_recovery
from execution.recovery_runtime_gate import evaluate_recovery_runtime


def build_record(status: str) -> ExecutionAuditRecord:
    intent = OrderIntent(
        symbol="NIFTY",
        option_type="CE",
        strike=25000,
        action=ExecutionAction.BUY,
        quantity=75,
        limit_price=120.0,
        client_order_id=f"qn-health-{status.lower()}",
    )
    result = ExecutionResult(status=ExecutionStatus(status), intent=intent)
    return ExecutionAuditRecord.from_result(result)


def test_recovery_runtime_health_state_blocks_when_reconciliation_is_missing():
    recovery = evaluate_recovery(build_record("UNKNOWN"))
    decision = evaluate_recovery_runtime(recovery)

    health = SimpleNamespace(
        ready=decision.safe_to_continue,
        requires_reconciliation=decision.requires_reconciliation,
        requires_manual_resolution=decision.requires_manual_resolution,
        reason=decision.reason,
    )

    assert health.ready is False
    assert health.requires_reconciliation is True
    assert health.requires_manual_resolution is False
    assert "reconciliation" in health.reason.lower()


def test_recovery_runtime_health_state_is_ready_for_terminal_execution():
    recovery = evaluate_recovery(build_record("EXECUTED"))
    decision = evaluate_recovery_runtime(recovery)

    health = SimpleNamespace(
        ready=decision.safe_to_continue,
        requires_reconciliation=decision.requires_reconciliation,
        requires_manual_resolution=decision.requires_manual_resolution,
        reason=decision.reason,
    )

    assert health.ready is True
    assert health.requires_reconciliation is False
    assert health.requires_manual_resolution is False


def test_sqlite_pending_recovery_provides_explicit_health_input(tmp_path):
    db_path = tmp_path / "health.sqlite"
    store = SQLiteExecutionAuditStore(db_path)
    store.append(build_record("UNKNOWN"))

    pending = store.load_pending()
    recovery = evaluate_recovery(pending[0])
    decision = evaluate_recovery_runtime(recovery)
    store.close()

    assert len(pending) == 1
    assert decision.safe_to_continue is False
    assert decision.requires_reconciliation is True
