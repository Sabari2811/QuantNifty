from __future__ import annotations

from dataclasses import dataclass

from execution.execution_audit_store import ExecutionAuditRecord
from execution.execution_recovery import evaluate_recovery
from execution.reconciliation import ReconciliationStatus


@dataclass(frozen=True, slots=True)
class RecoveryRuntimeDecision:
    safe_to_continue: bool
    requires_reconciliation: bool
    requires_manual_resolution: bool
    reason: str


def evaluate_recovery_runtime(
    record: ExecutionAuditRecord | None,
    reconciliation_report=None,
) -> RecoveryRuntimeDecision:
    """Translate persisted recovery state into an explicit runtime disposition."""
    decision = evaluate_recovery(record)

    if decision.requires_reconciliation:
        if reconciliation_report is None:
            return RecoveryRuntimeDecision(
                safe_to_continue=False,
                requires_reconciliation=True,
                requires_manual_resolution=False,
                reason="Persisted execution outcome is ambiguous; broker reconciliation is required before continuation.",
            )
        if reconciliation_report.status is ReconciliationStatus.MATCH:
            return RecoveryRuntimeDecision(
                safe_to_continue=True,
                requires_reconciliation=False,
                requires_manual_resolution=False,
                reason="Persisted ambiguous execution reconciled to broker state.",
            )
        if reconciliation_report.status is ReconciliationStatus.MISMATCH:
            return RecoveryRuntimeDecision(
                safe_to_continue=False,
                requires_reconciliation=True,
                requires_manual_resolution=True,
                reason="Recovery reconciliation mismatch requires manual resolution before continuation.",
            )
        return RecoveryRuntimeDecision(
            safe_to_continue=False,
            requires_reconciliation=True,
            requires_manual_resolution=False,
            reason="Recovery reconciliation remains unknown; continuation is blocked.",
        )

    return RecoveryRuntimeDecision(
        safe_to_continue=decision.safe_to_continue,
        requires_reconciliation=decision.requires_reconciliation,
        requires_manual_resolution=decision.requires_manual_resolution,
        reason=decision.reason,
    )
