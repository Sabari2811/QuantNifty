from __future__ import annotations

from types import SimpleNamespace

from execution.execution_contract import ExecutionStatus
from execution.execution_recovery import RecoveryDecision
from execution.recovery_runtime_gate import evaluate_recovery_runtime


def test_recovery_certification_requires_resolution_for_ambiguous_state():
    recovery = RecoveryDecision(
        safe_to_continue=False,
        requires_reconciliation=True,
        requires_manual_resolution=False,
        reason="Persisted execution outcome is ambiguous; broker reconciliation is required before continuation.",
    )

    decision = evaluate_recovery_runtime(
        recovery,
        reconciliation_report=None,
    )

    assert decision.safe_to_continue is False
    assert decision.requires_reconciliation is True
    assert decision.requires_manual_resolution is False


def test_recovery_certification_allows_matched_state():
    recovery = RecoveryDecision(
        safe_to_continue=False,
        requires_reconciliation=True,
        requires_manual_resolution=False,
        reason="Persisted execution outcome is ambiguous; broker reconciliation is required before continuation.",
    )

    decision = evaluate_recovery_runtime(
        recovery,
        reconciliation_report=SimpleNamespace(status=SimpleNamespace(value="MATCH")),
    )

    assert decision.safe_to_continue is False
