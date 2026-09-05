from __future__ import annotations

from dataclasses import dataclass

from execution.position_state import PositionState, PositionStatus


@dataclass(frozen=True, slots=True)
class PositionRecoveryDecision:
    safe_to_continue: bool
    requires_reconciliation: bool
    requires_manual_resolution: bool
    reason: str


def evaluate_position_recovery(position: PositionState | None) -> PositionRecoveryDecision:
    """Evaluate persisted canonical position state without inventing broker state."""
    if position is None:
        return PositionRecoveryDecision(
            False,
            False,
            False,
            "No persisted position state available.",
        )

    if position.status is PositionStatus.OPEN:
        return PositionRecoveryDecision(
            False,
            True,
            False,
            "Persisted open position requires broker reconciliation before continuation.",
        )

    if position.status is PositionStatus.CLOSED:
        return PositionRecoveryDecision(
            True,
            False,
            False,
            "Persisted position is terminal and closed.",
        )

    return PositionRecoveryDecision(
        False,
        True,
        True,
        "Persisted position state is unknown and requires manual resolution.",
    )


def recover_open_positions(store) -> tuple[PositionState, ...]:
    """Return persisted open canonical positions for broker reconciliation."""
    return tuple(store.open_positions())
