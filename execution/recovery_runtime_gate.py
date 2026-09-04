from __future__ import annotations

from dataclasses import dataclass

from execution.execution_audit_store import ExecutionAuditRecord
from execution.execution_recovery import evaluate_recovery


@dataclass(frozen=True, slots=True)
class RecoveryRuntimeDecision:
    safe_to_continue: bool
    requires_reconciliation: bool
    requires_manual_resolution: bool
    reason: str


def evaluate_recovery_runtime(
    record: ExecutionAuditRecord | None,
) -> RecoveryRuntimeDecision:
    """Translate persisted recovery state into an explicit runtime disposition."""
    decision = evaluate_recovery(record)
    return RecoveryRuntimeDecision(
        safe_to_continue=decision.safe_to_continue,
        requires_reconciliation=decision.requires_reconciliation,
        requires_manual_resolution=decision.requires_manual_resolution,
        reason=decision.reason,
    )
