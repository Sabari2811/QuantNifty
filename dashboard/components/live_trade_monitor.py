from __future__ import annotations

from dataclasses import asdict, is_dataclass
from enum import Enum
from math import isfinite
from typing import Any

import pandas as pd
import streamlit as st

from providers.indmoney_provider import INDMoneyProvider


_REFRESH_SECONDS = 5
_PRICE_KEYS = ("live_price", "ltp", "LTP", "last_price", "lastPrice", "close")


def _plain(value: Any) -> Any:
    if is_dataclass(value):
        return _plain(asdict(value))
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {str(k): _plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(v) for v in value]
    return value


def _num(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if isfinite(number) else None


def _first(mapping: Any, *keys: str) -> Any:
    if not isinstance(mapping, dict):
        return None
    for key in keys:
        if mapping.get(key) not in (None, ""):
            return mapping[key]
    return None


def _position_is_open(position: Any) -> bool:
    if position is None:
        return False
    if isinstance(position, dict):
        quantity = _num(_first(position, "quantity", "qty", "net_quantity", "net_qty"))
        if quantity is not None:
            return quantity != 0
        status = str(_first(position, "status", "state") or "").upper()
        return status in {"OPEN", "ACTIVE"}
    quantity = _num(getattr(position, "quantity", getattr(position, "qty", None)))
    if quantity is not None:
        return quantity != 0
    status = str(getattr(position, "status", "") or "").upper()
    return status in {"OPEN", "ACTIVE"}


def _position_value(position: Any, *keys: str) -> Any:
    if isinstance(position, dict):
        return _first(position, *keys)
    for key in keys:
        value = getattr(position, key, None)
        if value not in (None, ""):
            return value
    return None


def _option_row(chain: pd.DataFrame | None, strike: Any, option_type: str) -> dict[str, Any] | None:
    if not isinstance(chain, pd.DataFrame) or chain.empty:
        return None
    target = _num(strike)
    if target is None or "Strike" not in chain.columns:
        return None
    try:
        rows = chain[pd.to_numeric(chain["Strike"], errors="coerce") == target]
    except Exception:
        return None
    if rows.empty:
        return None
    row = rows.iloc[0].to_dict()
    suffix = str(option_type or "").upper().strip()
    if suffix not in {"CE", "PE"}:
        return None
    return {
        "security_id": row.get(f"{suffix}_ID"),
        "ltp": row.get(f"{suffix}_LTP"),
        "bid": row.get(f"{suffix}_BID"),
        "ask": row.get(f"{suffix}_ASK"),
    }


def _quote_price(provider: INDMoneyProvider, security_id: Any) -> tuple[float | None, Any]:
    sid = _num(security_id)
    if sid is None:
        return None, None
    try:
        quote = provider.get_quote(int(sid))
    except Exception:
        return None, None
    return _num(_first(quote, *_PRICE_KEYS)), _first(quote, "provider_timestamp", "timestamp", "exchange_timestamp", "last_trade_time")


def _trade_values(dashboard: Any) -> dict[str, Any]:
    plan = dashboard.trade_plan or {}
    intent = dashboard.execution_intent
    result = dashboard.execution_result
    position = dashboard.position
    trade = getattr(getattr(dashboard, "decision", None), "trade", None)

    option_type = str(
        _first(plan, "option_type", "optionType")
        or getattr(intent, "option_type", "")
        or getattr(trade, "option_type", "")
        or ""
    ).upper()
    strike = _num(
        _first(plan, "recommended_strike", "strike")
        or getattr(intent, "strike", None)
        or getattr(trade, "strike", None)
    )
    entry = _num(
        _first(plan, "entry", "premium_entry", "entry_price")
        or getattr(result, "average_fill_price", None)
        or getattr(intent, "limit_price", None)
        or getattr(trade, "entry", None)
    )
    stop_loss = _num(_first(plan, "stop_loss", "premium_stop_loss", "sl", "sl_price") or getattr(trade, "stop_loss", None))
    target1 = _num(_first(plan, "target1", "premium_target1", "target_1") or getattr(trade, "target1", None))
    target2 = _num(_first(plan, "target2", "premium_target2", "target_2") or getattr(trade, "target2", None))
    quantity = _num(
        getattr(result, "filled_quantity", None)
        or getattr(intent, "quantity", None)
        or _first(plan, "quantity", "qty", "total_quantity")
        or getattr(trade, "quantity", None)
        or _position_value(position, "quantity", "qty", "net_quantity", "net_qty")
    )
    if quantity is not None:
        quantity = int(quantity)

    exit_price = _num(
        _position_value(position, "exit_price", "average_exit_price", "close_price")
        or _position_value(getattr(dashboard, "last_trade", None), "exit_price", "average_exit_price", "close_price")
    )
    return {
        "option_type": option_type,
        "strike": strike,
        "entry": entry,
        "stop_loss": stop_loss,
        "target1": target1,
        "target2": target2,
        "quantity": quantity,
        "exit_price": exit_price,
        "open": _position_is_open(position),
    }


def _render_snapshot(dashboard: Any) -> None:
    values = _trade_values(dashboard)
    plan = dashboard.trade_plan or {}
    signal = str(plan.get("signal") or "WAIT").upper()
    option_type = values["option_type"] or "—"
    strike = values["strike"]
    entry = values["entry"]
    stop_loss = values["stop_loss"]
    target1 = values["target1"]
    target2 = values["target2"]
    quantity = values["quantity"]

    row = _option_row(dashboard.option_chain, strike, option_type)
    chain_price = _num(row.get("ltp")) if row else None
    security_id = row.get("security_id") if row else None
    live_price = chain_price
    provider_timestamp = None
    source = "option-chain quote"

    if values["open"] and security_id is not None:
        live_price, provider_timestamp = _quote_price(INDMoneyProvider(), security_id)
        if live_price is not None:
            source = "direct option quote"

    # A current quote is only displayed when the provider supplied it. There is
    # deliberately no last-value or synthetic-price fallback for the monitor.
    pnl = None
    if values["open"] and entry is not None and live_price is not None and quantity:
        pnl = (live_price - entry) * quantity

    trade_amount = entry * quantity if entry is not None and quantity else None
    status = "OPEN" if values["open"] else (str(getattr(getattr(dashboard, "execution_result", None), "status", "") or "").upper() or "NO ACTIVE TRADE")

    st.subheader("📡 Live Trade Monitor")
    st.caption(f"NIFTY • refreshes every {_REFRESH_SECONDS}s • prices are provider observations only")

    if signal in {"BUY_CALL", "BUY_PUT"} and not values["open"]:
        st.info("AI execution suggestion is active; no paper position is currently open.")
    elif not values["open"]:
        st.info("No active paper trade. The latest executable suggestion is shown below when available.")

    cols = st.columns(7, gap="small")
    cols[0].metric("Status", status)
    cols[1].metric("Strike", f"{strike:g}" if strike is not None else "—", option_type)
    cols[2].metric("Entry", f"₹{entry:,.2f}" if entry is not None else "—")
    cols[3].metric("Current LTP", f"₹{live_price:,.2f}" if live_price is not None else "UNAVAILABLE")
    cols[4].metric("P&L", f"₹{pnl:,.2f}" if pnl is not None else "—")
    cols[5].metric("Target 1", f"₹{target1:,.2f}" if target1 is not None else "—")
    cols[6].metric("Stop Loss", f"₹{stop_loss:,.2f}" if stop_loss is not None else "—")

    detail = st.columns(5, gap="small")
    detail[0].metric("Target 2", f"₹{target2:,.2f}" if target2 is not None else "—")
    detail[1].metric("Quantity", f"{quantity:,}" if quantity is not None else "—")
    detail[2].metric("Trade Amount", f"₹{trade_amount:,.2f}" if trade_amount is not None else "—")
    detail[3].metric("Exit Price", f"₹{values['exit_price']:,.2f}" if values["exit_price"] is not None else "—")
    detail[4].metric("Live Source", source if live_price is not None else "NO LIVE QUOTE")

    if provider_timestamp is not None:
        st.caption(f"Provider timestamp: {provider_timestamp}")
    elif live_price is None:
        st.warning("Current option price is unavailable from the provider; the monitor will not estimate it.")

    with st.expander("Execution suggestion / audit details", expanded=False):
        st.json({
            "signal": signal,
            "option_type": option_type,
            "strike": strike,
            "entry_price": entry,
            "stop_loss": stop_loss,
            "target1": target1,
            "target2": target2,
            "quantity": quantity,
            "trade_amount": trade_amount,
            "current_price": live_price,
            "exit_price": values["exit_price"],
            "pnl": pnl,
            "quote_security_id": security_id,
            "quote_source": source if live_price is not None else None,
            "execution_result": _plain(dashboard.execution_result),
        })


def render(dashboard: Any) -> None:
    """Render a live quote-only monitor without creating a new decision cycle.

    The fragment refreshes only this component, so it does not repeatedly invoke
    the decision engine or submit another trade. The main dashboard remains the
    canonical decision snapshot while the active option LTP/P&L is refreshed.
    """
    @st.fragment(run_every=f"{_REFRESH_SECONDS}s")
    def _fragment() -> None:
        _render_snapshot(dashboard)

    _fragment()
