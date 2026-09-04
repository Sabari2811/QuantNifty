from __future__ import annotations

from types import SimpleNamespace

from execution.execution_contract import ExecutionStatus
from execution.execution_recovery import RecoveryDecision
from execution.recovery_runtime_gate import evaluate_recovery_runtime
from execution.reconciliation import ReconciliationStatus


def recovery(safe_to_continue, requires_reconciliation, requires_manual_resolution=False):
    return RecoveryDecision(
        safe_to_continue=safe_to_continue,
        requires_reconciliation=requires_reconciliation,
        requires_manual_resolution=requires_manual_resolution,
        reason="test",
    )


def report(status):
    return SimpleNamespace(status=status)


def test_terminal_executed_resumes_without_reconciliation():
    decision = evaluate_recovery_runtime(recovery(True, False))

    assert decision.safe_to_continue is True
    assert decision.requires_reconciliation is False
    assert decision.requires_manual_resolution is False


def test_ambiguous_state_requires_reconciliation():
    decision = evaluate_recovery_runtime(recovery(False, True), reconciliation_report=None)

    assert decision.safe_to_continue is False
    assert decision.requires_reconciliation is True
    assert decision.requires_manual_resolution is False


def test_ambiguous_state_resumes_after_match():
    decision = evaluate_recovery_runtime(
        recovery(False, True),
        reconciliation_report=report(ReconciliationStatus.MATCH),
    )

    assert decision.safe_to_continue is True
    assert decision.requires_reconciliation is False
    assert decision.requires_manual_resolution is False


def test_ambiguous_state_requires_manual_resolution_on_mismatch():
    decision = evaluate_recovery_runtime(
        recovery(False, True),
        reconciliation_report=report(ReconciliationStatus.MISMATCH),
    )

    assert decision.safe_to_continue is False
    assert decision.requires_reconciliation is True
    assert decision.requires_manual_resolution is True


def test_ambiguous_state_remains_blocked_when_reconciliation_is_unknown():
    decision = evaluate_recovery_runtime(
        recovery(False, True),
        reconciliation_report=report(ReconciliationStatus.UNKNOWN),
    )

    assert decision.safe_to_continue is False
    assert decision.requires_reconciliation is True
    assert decision.requires_manual_resolution is False
