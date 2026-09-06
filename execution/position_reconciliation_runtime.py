from __future__ import annotations

from dataclasses import dataclass

from execution.reconciliation import ReconciliationStatus


@dataclass(frozen=True, slots=True)
class PositionReconciliationRuntimeDecision:
    safe_to_continue: bool
    requires_manual_resolution: bool
    reason: str


def evaluate_position_reconciliation_runtime(
    recovery,
    reconciliation_report=None,
) -> PositionReconciliationRuntimeDecision:
    """Gate continuation of a recovered position on explicit reconciliation.

    Accepts the persisted-position recovery runtime decision so an open
    recovered position cannot continue merely because it was loaded.
    """
    if recovery is None:
        return PositionReconciliationRuntimeDecision(
            False,
            False,
            "Position recovery decision is unavailable.",
        )

    positions = tuple(getattr(recovery, "positions", ()) or ())
    if not positions:
        return PositionReconciliationRuntimeDecision(
            bool(getattr(recovery, "safe_to_continue", False)),
            False,
            getattr(recovery, "reason", "No recovered positions require reconciliation."),
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
