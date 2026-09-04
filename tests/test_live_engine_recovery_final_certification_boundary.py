from __future__ import annotations

from types import SimpleNamespace

from execution.execution_contract import ExecutionStatus
from execution.execution_recovery import evaluate_recovery
from execution.recovery_runtime_gate import evaluate_recovery_runtime
from execution.reconciliation import ReconciliationStatus


def build_record(status: str):
    from execution.execution_audit_store import ExecutionAuditRecord
    from execution.execution_contract import ExecutionAction, ExecutionResult, OrderIntent

    intent = OrderIntent(
        symbol="NIFTY",
        option_type="CE",
        strike=25000,
        action=ExecutionAction.BUY,
        quantity=75,
        limit_price=120.0,
        client_order_id=f"qn-cert-{status.lower()}",
    )
    result = ExecutionResult(status=ExecutionStatus(status), intent=intent)
    return ExecutionAuditRecord.from_result(result)


def test_recovery_final_boundary_requires_match_for_ambiguous_execution():
    recovery = evaluate_recovery(build_record("UNKNOWN"))

    blocked = evaluate_recovery_runtime(recovery, reconciliation_report=None)
    assert blocked.safe_to_continue is False
    assert blocked.requires_reconciliation is True

    matched = evaluate_recovery_runtime(
        recovery,
        reconciliation_report=SimpleNamespace(status=ReconciliationStatus.MATCH),
    )
    assert matched.safe_to_continue is True
    assert matched.requires_reconciliation is False


def test_recovery_final_boundary_requires_manual_resolution_on_mismatch():
    recovery = evaluate_recovery(build_record("UNKNOWN"))
    decision = evaluate_recovery_runtime(
        recovery,
        reconciliation_report=SimpleNamespace(status=ReconciliationStatus.MISMATCH),
    )

    assert decision.safe_to_continue is False
    assert decision.requires_reconciliation is True
    assert decision.requires_manual_resolution is True


def test_recovery_final_boundary_preserves_terminal_execution_disposition():
    recovery = evaluate_recovery(build_record("EXECUTED"))
    decision = evaluate_recovery_runtime(recovery, reconciliation_report=None)

    assert decision.safe_to_continue is True
    assert decision.requires_reconciliation is False
    assert decision.requires_manual_resolution is False
