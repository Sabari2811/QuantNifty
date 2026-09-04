from __future__ import annotations

from dataclasses import dataclass

from execution.execution_contract import ExecutionResult, ExecutionStatus
from execution.reconciliation import ReconciliationReport, ReconciliationStatus


@dataclass(frozen=True, slots=True)
class ReconciliationGateDecision:
    allowed: bool
    reason: str


def evaluate_reconciliation_gate(
    result: ExecutionResult,
    report: ReconciliationReport | None,
) -> ReconciliationGateDecision:
    """Allow continuation/retry only after a known, matching broker state."""
    if result.status not in (ExecutionStatus.UNKNOWN, ExecutionStatus.SUBMITTED):
        return ReconciliationGateDecision(True, "Reconciliation is not required for this execution status.")

    if report is None:
        return ReconciliationGateDecision(False, "Execution outcome is ambiguous; reconciliation report is required.")
    if report.status is ReconciliationStatus.MATCH:
        return ReconciliationGateDecision(True, "Execution state reconciled successfully.")
    if report.status is ReconciliationStatus.MISMATCH:
        return ReconciliationGateDecision(False, "Execution state mismatch; manual resolution is required before retry.")
    return ReconciliationGateDecision(False, "Execution state remains unknown; retry is blocked pending reconciliation.")
