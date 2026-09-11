from __future__ import annotations

from hashlib import sha256

from decision.nifty_policy import NiftyPolicy
from execution.execution_contract import ExecutionAction, OrderIntent


POLICY = NiftyPolicy()


def build_order_intent(decision, *, source: str = "decision") -> OrderIntent | None:
    """Create an executable order intent for NIFTY CE/PE only."""
    if decision is None or not getattr(decision, "valid", False):
        return None

    signal = getattr(getattr(decision, "signal", None), "name", "")
    if signal == "WAIT":
        return None

    trade = getattr(decision, "trade", None)
    execution = getattr(trade, "execution", None) if trade is not None else None
    if trade is None or execution is None:
        return None

    ok, _ = POLICY.validate_symbol(getattr(trade, "symbol", "NIFTY"))
    if not ok:
        return None
    ok, _ = POLICY.validate_option(getattr(trade, "option_type", ""))
    if not ok:
        return None
    ok, _ = POLICY.validate_delta(getattr(getattr(trade, "contract", None), "delta", None))
    if not ok:
        return None

    quantity = int(getattr(execution, "lot_size", 0)) * int(getattr(execution, "lots", 0))
    if quantity <= 0:
        return None

    if signal in {"BUY CALL", "BUY PUT"}:
        action = ExecutionAction.BUY
    else:
        return None

    symbol = POLICY.symbol
    option_type = str(getattr(trade, "option_type", ""))
    strike = float(getattr(trade, "strike", 0))
    limit_price = float(getattr(trade, "entry", 0))
    contract = getattr(trade, "contract", None)
    expiry = str(getattr(contract, "expiry", "") or "")

    identity = "|".join((
        source,
        symbol,
        option_type,
        f"{strike:.8f}",
        action.value,
        str(quantity),
        f"{limit_price:.8f}",
        str(getattr(decision, "strategy_name", "")),
        expiry,
    ))
    client_order_id = "qn-" + sha256(identity.encode("utf-8")).hexdigest()[:24]

    return OrderIntent(
        symbol=symbol,
        option_type=option_type,
        strike=strike,
        action=action,
        quantity=quantity,
        limit_price=limit_price,
        strategy_name=str(getattr(decision, "strategy_name", "")),
        source=source,
        client_order_id=client_order_id,
        metadata={
            "signal": signal,
            "expiry": expiry,
            "underlying": POLICY.symbol,
            "max_trade_underlying_move": POLICY.max_trade_move,
            "overnight_position": False,
        },
    )
