from __future__ import annotations

from datetime import datetime
from typing import Any

from execution.position_state import PositionState, PositionStatus


def paper_position_to_state(position: Any) -> PositionState:
    """Map the existing paper runtime position into canonical PositionState."""
    order = getattr(position, "order", None)
    if order is None:
        raise ValueError("Position is missing its order")

    status = PositionStatus.CLOSED if bool(getattr(position, "closed", False)) else PositionStatus.OPEN
    closed_at = getattr(position, "exit_time", None)
    return PositionState(
        client_order_id=str(getattr(order, "order_id", "")).strip(),
        broker_order_id=str(getattr(order, "broker_order_id", "")).strip(),
        symbol=str(getattr(order, "symbol", "NIFTY")),
        option_type=str(getattr(order, "option_type", "")),
        strike=float(getattr(order, "strike")),
        quantity=int(getattr(order, "quantity")),
        entry_price=float(getattr(order, "entry_price")),
        current_price=float(getattr(position, "current_price", getattr(order, "entry_price", 0.0))),
        stop_loss=_optional_float(getattr(position, "stop_loss", None)),
        target=_optional_float(getattr(position, "target", None)),
        trailing_stop=_optional_float(getattr(position, "trailing_stop", None)),
        status=status,
        opened_at=getattr(order, "order_time", None),
        closed_at=closed_at if status is PositionStatus.CLOSED else None,
    )


def broker_position_to_state(position: Any) -> PositionState:
    """Map a broker position object into canonical PositionState."""
    status_raw = str(getattr(position, "status", "OPEN")).strip().upper()
    status = PositionStatus(status_raw) if status_raw in PositionStatus._value2member_map_ else PositionStatus.UNKNOWN
    return PositionState(
        client_order_id=str(getattr(position, "client_order_id", "") or getattr(position, "order_id", "")).strip(),
        broker_order_id=str(getattr(position, "broker_order_id", "") or getattr(position, "position_id", "")).strip(),
        symbol=str(getattr(position, "symbol", "")),
        option_type=str(getattr(position, "option_type", "")),
        strike=float(getattr(position, "strike")),
        quantity=int(getattr(position, "quantity")),
        entry_price=float(getattr(position, "entry_price", getattr(position, "avg_price", 0.0))),
        current_price=float(getattr(position, "current_price", getattr(position, "avg_price", 0.0))),
        status=status,
        closed_at=None if status is not PositionStatus.CLOSED else getattr(position, "closed_at", None),
    )


def _optional_float(value: Any) -> float | None:
    return None if value is None else float(value)
