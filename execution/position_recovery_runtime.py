from __future__ import annotations

from dataclasses import dataclass

from execution.position_state import PositionState
from execution.position_state_store import SQLitePositionStateStore


@dataclass(frozen=True, slots=True)
class PositionRecoveryRuntimeDecision:
    positions: tuple[PositionState, ...]
    safe_to_continue: bool
    reason: str


def recover_open_positions(store: SQLitePositionStateStore) -> PositionRecoveryRuntimeDecision:
    """Load persisted canonical open positions without mutating broker state."""
    if store is None:
        return PositionRecoveryRuntimeDecision(
            positions=(),
            safe_to_continue=False,
            reason="Position state store is unavailable.",
        )

    positions = tuple(store.open_positions())
    return PositionRecoveryRuntimeDecision(
        positions=positions,
        safe_to_continue=True,
        reason="Persisted canonical open positions loaded.",
    )
