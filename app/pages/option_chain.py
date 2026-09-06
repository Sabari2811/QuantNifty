import math

import streamlit as st

from app.services.live_service import LiveService

from app.components.market_summary import show as market_summary
from app.components.live_option_chain import show as live_option_chain


def _get_live_service():

    if "quantnifty_live_service" not in st.session_state:
        st.session_state["quantnifty_live_service"] = LiveService()

    return st.session_state["quantnifty_live_service"]


def _display_value(mapping, key, unavailable="—"):
    """Return a canonical summary value without inventing missing data."""
    if not isinstance(mapping, dict) or key not in mapping:
        return unavailable

    value = mapping[key]
    if value is None:
        return unavailable

    if isinstance(value, float) and not math.isfinite(value):
        return unavailable

    return value


def _flow_count(flow, key):
    """Display a flow count only when the canonical field exists."""
    value = _display_value(flow, key)
    if value == "—":
        return value
    try:
        return int(value)
    except (TypeError, ValueError):
        return "—"


def _recognized_flow_count(call, put):
    keys = (
        "long_buildup",
        "short_buildup",
        "long_unwinding",
        "short_covering",
    )
    total = 0
    for flow in (call, put):
        for key in keys:
            value = _flow_count(flow, key)
            if value != "—":
                total += value
    return total


def _unknown_flow_count(call, put):
    total = 0
    for flow in (call, put):
        value = _flow_count(flow, "unknown")
        if value != "—":
            total += value
    return total


def show():

    service = _get_live_service()

    ctx = service.get_context()

    st.title("📊 Option Chain")

    # ==========================================================
    # Runtime Controls
    # ==========================================================

    c1, c2, c3 = st.columns([1, 1, 4])

    with c1:
        if st.button(
            "🔄 Refresh",
            use_container_width=True,
        ):
            ctx = service.refresh()

    with c2:
        engine = service.runtime.get_engine()

        previous = getattr(
            engine,
            "_previous_greeks_df",
            None,
        )

        # The OI engine is the authoritative source for the current
        # history state. A previous snapshot alone does not mean that
        # recognizable OI flow has been detected.
        analytics = ctx.analytics or {}
        oi = analytics.get(
            "oi_flow",
            {},
        )
        history_summary = oi.get(
            "summary",
            {},
        )

        history_status = history_summary.get(
            "status",
            None,
        )

        if history_status == "AWAITING_PREVIOUS_SNAPSHOT":
            oi_history_state = "WAITING"

        elif history_status == "READY":
            call_history = history_summary.get(
                "call",
                {},
            )
            put_history = history_summary.get(
                "put",
                {},
            )

            recognized_flow_count = _recognized_flow_count(call_history, put_history)
            unknown_count = _unknown_flow_count(call_history, put_history)

            if recognized_flow_count == 0 and unknown_count > 0:
                oi_history_state = "NO CHANGE"
            else:
                oi_history_state = "READY"

        elif history_status is None and previous is None:
            oi_history_state = "WAITING"

        else:
            oi_history_state = "UNAVAILABLE"

        st.metric(
            "OI History",
            oi_history_state,
        )
    # ==========================================================
    # Market Summary
    # ==========================================================

    market_summary(ctx)

    st.divider()

    # ==========================================================
    # Live Option Chain
    # ==========================================================

    live_option_chain(ctx)

    st.divider()

    # ==========================================================
    # Open Interest Summary
    # ==========================================================

    analytics = ctx.analytics or {}

    oi = analytics.get(
        "oi_flow",
        {},
    )

    summary = oi.get(
        "summary",
        {},
    )

    call = summary.get(
        "call",
        {},
    )

    put = summary.get(
        "put",
        {},
    )

    oi_status = summary.get(
        "status",
        "UNKNOWN",
    )

    st.subheader("📈 Open Interest Summary")

    # ==========================================================
    # OI DATA AVAILABILITY
    # ==========================================================

    if oi_status == "AWAITING_PREVIOUS_SNAPSHOT":

        st.info(
            "⏳ OI Flow is waiting for the previous market snapshot. "
            "Refresh once more to calculate ΔPrice and ΔOI."
        )

    elif oi_status == "READY":

        c1, c2 = st.columns(2)

        with c1:
            st.metric(
                "Market Bias",
                _display_value(summary, "market_bias"),
            )

        with c2:
            st.metric(
                "OI Trend",
                _display_value(summary, "trend"),
            )

        # Distinguish a previous snapshot with no recognizable
        # flow from a snapshot containing actual OI flow.
        recognized_flow_count = _recognized_flow_count(call, put)
        unknown_count = _unknown_flow_count(call, put)

        if recognized_flow_count == 0 and unknown_count > 0:
            st.info(
                "ℹ️ No recognizable OI flow detected between the latest "
                "market snapshots. ΔPrice / ΔOI has not produced a "
                "valid flow classification yet."
            )

        # ======================================================
        # CALL FLOW
        # ======================================================

        st.markdown("### CALL FLOW")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Long Build-up",
            _flow_count(call, "long_buildup"),
        )

        c2.metric(
            "Short Build-up",
            _flow_count(call, "short_buildup"),
        )

        c3.metric(
            "Long Unwinding",
            _flow_count(call, "long_unwinding"),
        )

        c4.metric(
            "Short Covering",
            _flow_count(call, "short_covering"),
        )

        # ======================================================
        # PUT FLOW
        # ======================================================

        st.markdown("### PUT FLOW")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Long Build-up",
            _flow_count(put, "long_buildup"),
        )

        c2.metric(
            "Short Build-up",
            _flow_count(put, "short_buildup"),
        )

        c3.metric(
            "Long Unwinding",
            _flow_count(put, "long_unwinding"),
        )

        c4.metric(
            "Short Covering",
            _flow_count(put, "short_covering"),
        )
    else:

        st.warning(
            "OI Flow data is currently unavailable."
        )

    st.divider()

    # ==========================================================
    # Gamma Levels
    # ==========================================================

    dealer = analytics.get(
        "dealer",
        {},
    )

    st.subheader("🎯 Key Gamma Levels")

    a, b, c, d = st.columns(4)

    a.metric(
        "Gamma Flip",
        _display_value(dealer, "gamma_flip"),
    )

    b.metric(
        "Gamma Wall",
        _display_value(dealer, "gamma_wall"),
    )

    c.metric(
        "Call Wall",
        _display_value(dealer, "call_wall"),
    )

    d.metric(
        "Put Wall",
        _display_value(dealer, "put_wall"),
    )