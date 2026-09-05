from __future__ import annotations

from execution.execution_contract import ExecutionResult, ExecutionStatus
from execution.position_state import PositionState, PositionStatus


def position_state_from_execution_result(
    result: ExecutionResult | None,
    *,
    current_price: float | None = None,
    stop_loss: float | None = None,
    target: float | None = None,
    opened_at=None,
) -> PositionState | None:
    """Create canonical position state only from a successful execution result."""
    if result is None or result.status is not ExecutionStatus.EXECUTED:
        return None

    filled_quantity = int(result.filled_quantity or result.intent.quantity)
    entry_price = result.average_fill_price
    if entry_price is None:
        entry_price = result.intent.limit_price

    return PositionState(
        client_order_id=result.intent.client_order_id,
        broker_order_id=result.broker_order_id,
        symbol=result.intent.symbol,
        option_type=result.intent.option_type,
        strike=result.intent.strike,
        quantity=filled_quantity,
        entry_price=entry_price,
        current_price=entry_price if current_price is None else current_price,
        stop_loss=stop_loss,
        target=target,
        status=PositionStatus.OPEN,
        opened_at=opened_at or result.timestamp,
    )
