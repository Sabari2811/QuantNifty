from __future__ import annotations

from dataclasses import dataclass

from execution.reconciliation import ReconciliationStatus
from execution.position_recovery import PositionRecoveryDecision


@dataclass(frozen=True, slots=True)
class PositionReconciliationRuntimeDecision:
    safe_to_continue: bool
    requires_manual_resolution: bool
    reason: str


def evaluate_position_reconciliation_runtime(
    recovery: PositionRecoveryDecision | None,
    reconciliation_report=None,
) -> PositionReconciliationRuntimeDecision:
    """Gate continuation of a recovered position on explicit reconciliation."""
    if recovery is None:
        return PositionReconciliationRuntimeDecision(
            False,
            False,
            "Position recovery decision is unavailable.",
        )

    if not recovery.requires_reconciliation:
        return PositionReconciliationRuntimeDecision(
            recovery.safe_to_continue,
            recovery.requires_manual_resolution,
            recovery.reason,
        )

    if reconciliation_report is None:
        return PositionReconciliationRuntimeDecision(
            False,
            False,
            "Recovered position requires broker reconciliation before continuation.",
        )

    status = getattr(reconciliation_report, "status", None)
    if status is ReconciliationStatus.MATCH or status == "MATCH":
        return PositionReconciliationRuntimeDecision(
            True,
            False,
            "Recovered position reconciled to broker state.",
        )

    if status is ReconciliationStatus.MISMATCH or status == "MISMATCH":
        return PositionReconciliationRuntimeDecision(
            False,
            True,
            "Recovered position reconciliation mismatch requires manual resolution.",
        )

    return PositionReconciliationRuntimeDecision(
        False,
        False,
        "Recovered position reconciliation remains unknown; continuation is blocked.",
    )
