import streamlit as st

from app.services.live_service import LiveService

from app.components.market_summary import show as market_summary
from app.components.live_option_chain import show as live_option_chain


# ==========================================================
# PAGE
# ==========================================================

def show():

    service = LiveService()

    ctx = service.get_context()

    st.title("📊 Option Chain")

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

    analytics = ctx.analytics

    oi = analytics.get("oi_flow", {})

    summary = oi.get("summary", {})

    call = summary.get("call", {})
    put = summary.get("put", {})

    st.subheader("📈 Open Interest Summary")

    c1, c2 = st.columns(2)

    with c1:

        st.metric(
            "Market Bias",
            summary.get("market_bias", "-")
        )

    with c2:

        st.metric(
            "OI Trend",
            summary.get("trend", "-")
        )

    st.markdown("### CALL FLOW")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Long Build-up",
        call.get("long_buildup", 0)
    )

    c2.metric(
        "Short Build-up",
        call.get("short_buildup", 0)
    )

    c3.metric(
        "Long Unwinding",
        call.get("long_unwinding", 0)
    )

    c4.metric(
        "Short Covering",
        call.get("short_covering", 0)
    )

    st.markdown("### PUT FLOW")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Long Build-up",
        put.get("long_buildup", 0)
    )

    c2.metric(
        "Short Build-up",
        put.get("short_buildup", 0)
    )

    c3.metric(
        "Long Unwinding",
        put.get("long_unwinding", 0)
    )

    c4.metric(
        "Short Covering",
        put.get("short_covering", 0)
    )

    st.divider()

    # ==========================================================
    # Gamma Levels
    # ==========================================================

    dealer = analytics.get("dealer", {})

    st.subheader("🎯 Key Gamma Levels")

    a, b, c, d = st.columns(4)

    a.metric(
        "Gamma Flip",
        dealer.get("gamma_flip", "-")
    )

    b.metric(
        "Gamma Wall",
        dealer.get("gamma_wall", "-")
    )

    c.metric(
        "Call Wall",
        dealer.get("call_wall", "-")
    )

    d.metric(
        "Put Wall",
        dealer.get("put_wall", "-")
    )