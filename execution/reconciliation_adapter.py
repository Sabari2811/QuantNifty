from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from execution.reconciliation import PositionSnapshot, ReconciliationReport, reconcile_positions


def local_position_snapshot(position: Any) -> PositionSnapshot:
    """Map the canonical runtime paper position shape to reconciliation state."""
    order = getattr(position, "order", None)
    if order is None:
        raise ValueError("Position is missing its order identity")

    client_order_id = str(getattr(order, "order_id", "")).strip()
    if not client_order_id:
        raise ValueError("Position order_id is required for reconciliation")

    return PositionSnapshot(
        client_order_id=client_order_id,
        symbol=str(getattr(order, "symbol", "NIFTY")),
        option_type=str(getattr(order, "option_type", "")),
        strike=float(getattr(order, "strike")),
        quantity=int(getattr(order, "quantity")),
        status="CLOSED" if bool(getattr(position, "closed", False)) else str(getattr(order, "status", "OPEN")),
        broker_order_id=str(getattr(order, "broker_order_id", "")),
    )


def broker_position_snapshot(position: Any) -> PositionSnapshot:
    """Map a broker-facing position object to the reconciliation contract."""
    client_order_id = str(
        getattr(position, "client_order_id", "")
        or getattr(position, "order_id", "")
    ).strip()
    if not client_order_id:
        raise ValueError("Broker position client/order identity is required for reconciliation")

    return PositionSnapshot(
        client_order_id=client_order_id,
        symbol=str(getattr(position, "symbol", "")),
        option_type=str(getattr(position, "option_type", "")),
        strike=float(getattr(position, "strike")),
        quantity=int(getattr(position, "quantity")),
        status=str(getattr(position, "status", "OPEN")),
        broker_order_id=str(getattr(position, "broker_order_id", "")),
    )


def reconcile_runtime_positions(
    local_positions: Iterable[Any] | None,
    broker_positions: Iterable[Any] | None,
) -> ReconciliationReport:
    """Adapt runtime/broker positions into the canonical reconciliation contract."""
    local = None if local_positions is None else tuple(local_position_snapshot(p) for p in local_positions)
    broker = None if broker_positions is None else tuple(broker_position_snapshot(p) for p in broker_positions)
    return reconcile_positions(local, broker)
