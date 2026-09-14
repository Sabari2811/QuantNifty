from __future__ import annotations

from uuid import uuid4

from execution.execution_contract import ExecutionAction, OrderIntent


def build_order_intent(decision) -> OrderIntent | None:
    if decision is None or not getattr(decision, "valid", False):
        return None
    trade = getattr(decision, "trade", None)
    if trade is None:
        return None

    signal = str(getattr(getattr(decision, "signal", None), "name", ""))
    action = ExecutionAction.SELL if "SELL" in signal.upper() else ExecutionAction.BUY
    execution = getattr(trade, "execution", None)
    lots = int(getattr(execution, "lots", 1) or 1)
    lot_size = int(getattr(execution, "lot_size", 0) or 0)
    quantity = lots * lot_size
    if quantity <= 0:
        return None

    return OrderIntent(
        symbol=str(getattr(trade, "symbol", "NIFTY")),
        option_type=str(getattr(trade, "option_type", "")),
        strike=float(getattr(trade, "strike")),
        action=action,
        quantity=quantity,
        limit_price=float(getattr(trade, "entry")) if getattr(trade, "entry", None) is not None else None,
        strategy_name=str(getattr(decision, "strategy_name", "")),
        client_order_id=f"qn-{uuid4().hex}",
    )
