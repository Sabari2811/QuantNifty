from __future__ import annotations

from execution.position_lifecycle import PositionLifecycleAction
from execution.position_lifecycle_adapter import evaluate_paper_position_lifecycle
from execution.position_state import PositionState
from execution.position_state_store import SQLitePositionStateStore


class PositionRuntimeService:
    """Bridge canonical position state, persistence, lifecycle evaluation and paper runtime."""

    def __init__(self, store: SQLitePositionStateStore):
        if store is None:
            raise ValueError("Position state store is required")
        self.store = store

    def persist_paper_position(self, position) -> PositionState:
        state = _paper_position_to_state(position)
        self.store.save(state)
        return state

    def evaluate_paper_position(self, position, *, current_price=None, manual_close=False):
        return evaluate_paper_position_lifecycle(
            position,
            current_price=current_price,
            manual_close=manual_close,
        )

    def persist_after_lifecycle(self, position, lifecycle_decision, *, closed_at=None) -> PositionState:
        if lifecycle_decision.action is PositionLifecycleAction.HOLD:
            return self.persist_paper_position(position)

        if lifecycle_decision.action in {
            PositionLifecycleAction.CLOSE_STOP_LOSS,
            PositionLifecycleAction.CLOSE_TARGET,
            PositionLifecycleAction.CLOSE_MANUAL,
        }:
            state = _paper_position_to_state(position)
            if getattr(position, "closed", False):
                state = PositionState(
                    client_order_id=state.client_order_id,
                    broker_order_id=state.broker_order_id,
                    symbol=state.symbol,
                    option_type=state.option_type,
                    strike=state.strike,
                    quantity=state.quantity,
                    entry_price=state.entry_price,
                    current_price=state.current_price,
                    stop_loss=state.stop_loss,
                    target=state.target,
                    trailing_stop=state.trailing_stop,
                    status=state.status.CLOSED,
                    opened_at=state.opened_at,
                    closed_at=closed_at or getattr(position, "exit_time", None),
                )
            return self.store.save(state)

        raise ValueError(f"Unsupported lifecycle action: {lifecycle_decision.action}")


def _paper_position_to_state(position) -> PositionState:
    from execution.position_state_adapter import paper_position_to_state

    return paper_position_to_state(position)
