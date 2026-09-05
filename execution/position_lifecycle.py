from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from execution.position_state import PositionState, PositionStatus


class PositionLifecycleAction(str, Enum):
    HOLD = "HOLD"
    CLOSE_STOP_LOSS = "CLOSE_STOP_LOSS"
    CLOSE_TARGET = "CLOSE_TARGET"
    CLOSE_MANUAL = "CLOSE_MANUAL"


@dataclass(frozen=True, slots=True)
class PositionLifecycleDecision:
    action: PositionLifecycleAction
    reason: str


def evaluate_position_lifecycle(
    position: PositionState,
    *,
    current_price: float | None = None,
    manual_close: bool = False,
) -> PositionLifecycleDecision:
    """Evaluate close conditions without mutating canonical position state."""
    if position is None:
        raise ValueError("Position state is required")

    if manual_close:
        return PositionLifecycleDecision(
            PositionLifecycleAction.CLOSE_MANUAL,
            "Manual close requested.",
        )

    price = position.current_price if current_price is None else current_price
    if price < 0:
        raise ValueError("current_price must be non-negative")

    # A closed position must never be reopened by lifecycle evaluation.
    # Keep the canonical position lifecycle idempotent while allowing the
    # runtime adapter/service to classify the already-observed exit reason
    # from the current price for persistence/replay diagnostics.
    if position.status is PositionStatus.CLOSED:
        if position.target is not None and price >= position.target:
            return PositionLifecycleDecision(
                PositionLifecycleAction.CLOSE_TARGET,
                "Target reached on an already-closed position; no mutation required.",
            )
        if position.trailing_stop is not None and price <= position.trailing_stop:
            return PositionLifecycleDecision(
                PositionLifecycleAction.CLOSE_STOP_LOSS,
                "Trailing stop reached on an already-closed position; no mutation required.",
            )
        if position.stop_loss is not None and price <= position.stop_loss:
            return PositionLifecycleDecision(
                PositionLifecycleAction.CLOSE_STOP_LOSS,
                "Stop loss reached on an already-closed position; no mutation required.",
            )
        return PositionLifecycleDecision(
            PositionLifecycleAction.HOLD,
            "Position is not open.",
        )

    if position.status is not PositionStatus.OPEN:
        return PositionLifecycleDecision(
            PositionLifecycleAction.HOLD,
            "Position is not open.",
        )

    stop = position.trailing_stop if position.trailing_stop is not None else position.stop_loss
    if stop is not None and price <= stop:
        reason = "Trailing stop reached." if position.trailing_stop is not None else "Stop loss reached."
        return PositionLifecycleDecision(PositionLifecycleAction.CLOSE_STOP_LOSS, reason)

    if position.target is not None and price >= position.target:
        return PositionLifecycleDecision(
            PositionLifecycleAction.CLOSE_TARGET,
            "Target reached.",
        )

    return PositionLifecycleDecision(PositionLifecycleAction.HOLD, "No close condition reached.")
