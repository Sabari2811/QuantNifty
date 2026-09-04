from __future__ import annotations

from types import SimpleNamespace

from execution.execution_audit_store import ExecutionAuditRecord, InMemoryExecutionAuditStore
from execution.execution_contract import ExecutionAction, ExecutionResult, ExecutionStatus, OrderIntent
from execution.execution_recovery import evaluate_recovery
from execution.recovery_runtime_gate import RecoveryRuntimeDecision, evaluate_recovery_runtime


def build_record(status: str) -> ExecutionAuditRecord:
    intent = OrderIntent(
        symbol="NIFTY",
        option_type="CE",
        strike=25000,
        action=ExecutionAction.BUY,
        quantity=75,
        limit_price=120.0,
        client_order_id=f"qn-recovery-{status.lower()}",
    )
    result = ExecutionResult(status=ExecutionStatus(status), intent=intent)
    return ExecutionAuditRecord.from_result(result)


def test_recovery_runtime_blocks_ambiguous_persisted_state_without_broker_reconciliation():
    record = build_record("UNKNOWN")
    recovery = evaluate_recovery(record)
    decision = evaluate_recovery_runtime(recovery, reconciliation_report=None)

    assert decision.safe_to_continue is False
    assert decision.requires_reconciliation is True
    assert decision.requires_manual_resolution is False


def test_recovery_runtime_allows_terminal_executed_state():
    record = build_record("EXECUTED")
    recovery = evaluate_recovery(record)
    decision = evaluate_recovery_runtime(recovery, reconciliation_report=None)

    assert decision.safe_to_continue is True
    assert decision.requires_reconciliation is False
    assert decision.requires_manual_resolution is False
