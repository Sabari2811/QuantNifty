import streamlit as st

from app.services.live_service import LiveService

from app.components.market_summary import show as market_summary
from app.components.live_option_chain import show as live_option_chain


def _get_live_service():

    if "quantnifty_live_service" not in st.session_state:
        st.session_state["quantnifty_live_service"] = LiveService()

    return st.session_state["quantnifty_live_service"]


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

            recognized_flow_count = sum(
                call_history.get(key, 0)
                for key in (
                    "long_buildup",
                    "short_buildup",
                    "long_unwinding",
                    "short_covering",
                )
            ) + sum(
                put_history.get(key, 0)
                for key in (
                    "long_buildup",
                    "short_buildup",
                    "long_unwinding",
                    "short_covering",
                )
            )

            unknown_count = (
                call_history.get("unknown", 0)
                + put_history.get("unknown", 0)
            )

            if recognized_flow_count == 0 and unknown_count > 0:
                oi_history_state = "NO CHANGE"
            else:
                oi_history_state = "READY"

        elif previous is None:
            oi_history_state = "WAITING"

        else:
            oi_history_state = "READY"

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
                summary.get(
                    "market_bias",
                    "-",
                ),
            )

        with c2:
            st.metric(
                "OI Trend",
                summary.get(
                    "trend",
                    "-",
                ),
            )

        # Distinguish a previous snapshot with no recognizable
        # flow from a snapshot containing actual OI flow.
        recognized_flow_count = sum(
            call.get(key, 0)
            for key in (
                "long_buildup",
                "short_buildup",
                "long_unwinding",
                "short_covering",
            )
        ) + sum(
            put.get(key, 0)
            for key in (
                "long_buildup",
                "short_buildup",
                "long_unwinding",
                "short_covering",
            )
        )

        unknown_count = (
            call.get("unknown", 0)
            + put.get("unknown", 0)
        )

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
            call.get("long_buildup", 0),
        )

        c2.metric(
            "Short Build-up",
            call.get("short_buildup", 0),
        )

        c3.metric(
            "Long Unwinding",
            call.get("long_unwinding", 0),
        )

        c4.metric(
            "Short Covering",
            call.get("short_covering", 0),
        )

        # ======================================================
        # PUT FLOW
        # ======================================================

        st.markdown("### PUT FLOW")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Long Build-up",
            put.get("long_buildup", 0),
        )

        c2.metric(
            "Short Build-up",
            put.get("short_buildup", 0),
        )

        c3.metric(
            "Long Unwinding",
            put.get("long_unwinding", 0),
        )

        c4.metric(
            "Short Covering",
            put.get("short_covering", 0),
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
        dealer.get(
            "gamma_flip",
            "-",
        ),
    )

    b.metric(
        "Gamma Wall",
        dealer.get(
            "gamma_wall",
            "-",
        ),
    )

    c.metric(
        "Call Wall",
        dealer.get(
            "call_wall",
            "-",
        ),
    )

    d.metric(
        "Put Wall",
        dealer.get(
            "put_wall",
            "-",
        ),
    )