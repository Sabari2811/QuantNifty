from __future__ import annotations

from dataclasses import dataclass

from execution.execution_contract import ExecutionResult, ExecutionStatus
from execution.reconciliation import ReconciliationReport, ReconciliationStatus


@dataclass(frozen=True, slots=True)
class RuntimeReconciliationDecision:
    safe_to_continue: bool
    requires_manual_resolution: bool
    reason: str


def evaluate_runtime_reconciliation(
    result: ExecutionResult | None,
    report: ReconciliationReport | None,
) -> RuntimeReconciliationDecision:
    """Convert an execution result plus reconciliation report into a safe runtime disposition."""
    if result is None:
        return RuntimeReconciliationDecision(False, False, "Execution result is unavailable.")

    if result.status not in (ExecutionStatus.UNKNOWN, ExecutionStatus.SUBMITTED):
        return RuntimeReconciliationDecision(True, False, "Execution status does not require runtime reconciliation.")

    if report is None:
        return RuntimeReconciliationDecision(False, False, "Ambiguous execution requires a reconciliation report.")

    if report.status is ReconciliationStatus.MATCH:
        return RuntimeReconciliationDecision(True, False, "Ambiguous execution reconciled to broker state.")

    if report.status is ReconciliationStatus.MISMATCH:
        return RuntimeReconciliationDecision(False, True, "Reconciliation mismatch requires manual resolution before retry.")

    return RuntimeReconciliationDecision(False, False, "Reconciliation remains unknown; retry is blocked.")
