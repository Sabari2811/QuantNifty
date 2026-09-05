from types import SimpleNamespace

from execution.position_recovery import PositionRecoveryDecision
from execution.position_reconciliation_runtime import (
    evaluate_position_reconciliation_runtime,
)
from execution.reconciliation import ReconciliationStatus


def test_open_recovery_without_report_blocks():
    recovery = PositionRecoveryDecision(False, True, False, "needs reconcile")
    result = evaluate_position_reconciliation_runtime(recovery)
    assert result.safe_to_continue is False
    assert result.requires_manual_resolution is False


def test_open_recovery_match_allows_continuation():
    recovery = PositionRecoveryDecision(False, True, False, "needs reconcile")
    report = SimpleNamespace(status=ReconciliationStatus.MATCH)
    result = evaluate_position_reconciliation_runtime(recovery, report)
    assert result.safe_to_continue is True
    assert result.requires_manual_resolution is False


def test_open_recovery_mismatch_requires_manual_resolution():
    recovery = PositionRecoveryDecision(False, True, False, "needs reconcile")
    report = SimpleNamespace(status="MISMATCH")
    result = evaluate_position_reconciliation_runtime(recovery, report)
    assert result.safe_to_continue is False
    assert result.requires_manual_resolution is True


def test_open_recovery_unknown_stays_blocked():
    recovery = PositionRecoveryDecision(False, True, False, "needs reconcile")
    report = SimpleNamespace(status="UNKNOWN")
    result = evaluate_position_reconciliation_runtime(recovery, report)
    assert result.safe_to_continue is False
    assert result.requires_manual_resolution is False


def test_closed_recovery_preserves_terminal_safe_state():
    recovery = PositionRecoveryDecision(True, False, False, "closed")
    result = evaluate_position_reconciliation_runtime(recovery)
    assert result.safe_to_continue is True
    assert result.requires_manual_resolution is False


def test_unavailable_recovery_fails_closed():
    result = evaluate_position_reconciliation_runtime(None)
    assert result.safe_to_continue is False
