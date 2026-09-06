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

    A supplied broker reconciliation report is authoritative for the
    continuation decision. Recovery state is used only when no reconciliation
    report is available, so a successful MATCH cannot be masked by a stale or
    conservative recovery flag.
    """
    if recovery is None:
        return PositionReconciliationRuntimeDecision(
            False,
            False,
            "Position recovery decision is unavailable.",
        )

    if reconciliation_report is not None:
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

    positions = tuple(getattr(recovery, "positions", ()) or ())
    if not positions:
        return PositionReconciliationRuntimeDecision(
            bool(getattr(recovery, "safe_to_continue", False)),
            False,
            getattr(recovery, "reason", "No recovered positions require reconciliation."),
        )

    return PositionReconciliationRuntimeDecision(
        False,
        False,
        "Recovered position requires broker reconciliation before continuation.",
    )
