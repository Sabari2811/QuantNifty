from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from execution.position_lifecycle import (
    PositionLifecycleAction,
    PositionLifecycleDecision,
    evaluate_position_lifecycle,
)
from execution.position_state_adapter import paper_position_to_state


@dataclass(frozen=True, slots=True)
class PaperPositionLifecycleDecision:
    position: Any
    lifecycle: PositionLifecycleDecision


def evaluate_paper_position_lifecycle(
    position: Any,
    *,
    current_price: float | None = None,
    manual_close: bool = False,
) -> PaperPositionLifecycleDecision:
    state = paper_position_to_state(position)
    lifecycle = evaluate_position_lifecycle(
        state,
        current_price=current_price,
        manual_close=manual_close,
    )
    return PaperPositionLifecycleDecision(position=position, lifecycle=lifecycle)


def should_close_paper_position(
    position: Any,
    *,
    current_price: float | None = None,
    manual_close: bool = False,
) -> bool:
    decision = evaluate_paper_position_lifecycle(
        position,
        current_price=current_price,
        manual_close=manual_close,
    )
    return decision.lifecycle.action is not PositionLifecycleAction.HOLD
