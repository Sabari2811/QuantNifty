from __future__ import annotations

from typing import Any

import streamlit as st

from dashboard.components.live_trade_monitor import render as render_live_trade_monitor


def _value(mapping: Any, *keys: str, default: Any = "—") -> Any:
    if not isinstance(mapping, dict):
        return default
    for key in keys:
        value = mapping.get(key)
        if value not in (None, ""):
            return value
    return default


def _fmt(value: Any, prefix: str = "") -> str:
    if value in (None, "", "—"):
        return "—"
    try:
        return f"{prefix}{float(value):,.2f}"
    except (TypeError, ValueError):
        return str(value)


def _pct(value: Any) -> str:
    if value in (None, "", "—"):
        return "—"
    try:
        number = float(value)
        if abs(number) <= 1:
            number *= 100
        return f"{number:.1f}%"
    except (TypeError, ValueError):
        return str(value)


def _regime(dashboard: Any) -> str:
    dealer = dashboard.dealer
    return str(getattr(dealer, "market_mode", None) or "UNKNOWN").replace("_", " ").upper()


def _brain_status(dashboard: Any) -> str:
    observation = getattr(dashboard, "brain_observation", None)
    if observation is None:
        return "UNAVAILABLE"
    return str(getattr(observation, "status", None) or getattr(observation, "recommendation", None) or "ACTIVE").upper()


def render(dashboard: Any) -> None:
    """Render the primary one-screen NIFTY decision and trade cockpit.

    This is an additional presentation layer. It reuses the canonical
    DashboardData and existing live monitor; it never recomputes or mutates
    trading state and does not remove any existing terminal components.
    """
    dealer = dashboard.dealer
    liquidity = dashboard.liquidity or {}
    expected = dashboard.expected_move or {}
    probability = dashboard.probability or {}
    signal = dashboard.signal or {}
    plan = dashboard.trade_plan or {}
    risk = dashboard.risk or {}
    pcr = dashboard.pcr or {}
    max_pain = dashboard.max_pain or {}
    structure = dashboard.market_structure or {}
    imbalance = liquidity.get("order_imbalance", {}) if isinstance(liquidity, dict) else {}

    st.title("🎯 NIFTY Trade Cockpit")
    st.caption("Single-screen decision view • analytical context + execution plan + live position state")

    top = st.columns(6, gap="small")
    top[0].metric("NIFTY Spot", _fmt(dashboard.spot, "₹"))
    top[1].metric("Signal", str(_value(signal, "signal", default="WAIT")).upper())
    top[2].metric("Confidence", _pct(_value(signal, "confidence")))
    top[3].metric("Regime", _regime(dashboard))
    top[4].metric("Support", _fmt(getattr(dealer, "support", None)))
    top[5].metric("Resistance", _fmt(getattr(dealer, "resistance", None)))

    st.divider()
    st.subheader("Decision Map")
    row = st.columns(6, gap="small")
    row[0].metric("Liquidity Support", _fmt(_value(liquidity, "support", default=getattr(dealer, "support", None))))
    row[1].metric("Liquidity Resistance", _fmt(_value(liquidity, "resistance", default=getattr(dealer, "resistance", None))))
    row[2].metric("Call Wall", _fmt(_value(liquidity, "call_wall")))
    row[3].metric("Put Wall", _fmt(_value(liquidity, "put_wall")))
    row[4].metric("Gamma Flip", _fmt(getattr(dealer, "gamma_flip", None)))
    row[5].metric("Gamma Wall", _fmt(getattr(dealer, "gamma_wall", None)))

    row = st.columns(6, gap="small")
    row[0].metric("Dealer Gamma", str(getattr(dealer, "dealer_gamma", None) or "—"))
    row[1].metric("Dealer Flow", str(_value(dashboard.dealer_flow, "flow", "regime", "signal")))
    row[2].metric("OI PCR", _fmt(_value(imbalance, "oi_ratio")))
    row[3].metric("Volume PCR", _fmt(_value(imbalance, "volume_ratio")))
    row[4].metric("Max Pain", _fmt(_value(max_pain, "max_pain", "value")))
    row[5].metric("Structure", str(_value(structure, "regime", "structure", "bias")))

    st.subheader("Expected Move & Direction")
    row = st.columns(5, gap="small")
    row[0].metric("Expected Move", _fmt(_value(expected, "expected_move", "move")))
    row[1].metric("Upper", _fmt(_value(expected, "upper")))
    row[2].metric("Lower", _fmt(_value(expected, "lower")))
    row[3].metric("Bullish Probability", _pct(_value(probability, "bullish_probability", "bullish")))
    row[4].metric("Breakout Probability", _pct(getattr(dealer, "breakout_probability", None)))

    st.subheader("Trade Trigger")
    row = st.columns(7, gap="small")
    option_type = str(_value(plan, "option_type", default="—")).upper()
    row[0].metric("Action", str(_value(plan, "signal", default=signal.get("signal", "WAIT"))).upper())
    row[1].metric("Option", option_type)
    row[2].metric("Strike", _fmt(_value(plan, "recommended_strike", "strike")))
    row[3].metric("Entry", _fmt(_value(plan, "entry", "entry_price"), "₹"))
    row[4].metric("Stop Loss", _fmt(_value(plan, "stop_loss", "sl"), "₹"))
    row[5].metric("Target 1", _fmt(_value(plan, "target1", "target_1"), "₹"))
    row[6].metric("Target 2", _fmt(_value(plan, "target2", "target_2"), "₹"))

    row = st.columns(5, gap="small")
    row[0].metric("Risk / Reward", _fmt(_value(plan, "risk_reward", "rr")))
    row[1].metric("Risk State", str(_value(risk, "status", "state", "decision", default="—")).upper())
    row[2].metric("Brain", _brain_status(dashboard))
    row[3].metric("Trade Status", str(dashboard.trade_status or "—").upper())
    row[4].metric("Block Reason", str(dashboard.trade_block_reason or "NONE"))

    with st.container(border=True):
        render_live_trade_monitor(dashboard)

    st.caption(f"Expiry: {dashboard.expiry} • Provider: {dashboard.provider} • Runtime: {dashboard.runtime_status or '—'} • Cycle: {dashboard.cycle_no}")
