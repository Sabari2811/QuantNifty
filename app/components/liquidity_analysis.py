import streamlit as st

from app.utils.formatters import (
    format_strike,
    format_ratio,
)

from app.utils.badges import (
    pressure,
)


# ==========================================================
# HELPERS
# ==========================================================

def _liquidity(ctx):
    try:
        return ctx.analytics.get("liquidity", {})
    except Exception:
        return {}


# ==========================================================
# UI
# ==========================================================

def show(ctx):

    liquidity = _liquidity(ctx)

    st.subheader("💧 Liquidity Analysis")

    # ======================================================
    # Liquidity Walls
    # ======================================================

    st.markdown("#### Liquidity Walls")

    row1 = st.columns(4)

    row1[0].metric(
        "Support",
        format_strike(
            liquidity.get("support")
        )
    )

    row1[1].metric(
        "Resistance",
        format_strike(
            liquidity.get("resistance")
        )
    )

    row1[2].metric(
        "Call Wall",
        format_strike(
            liquidity.get("call_wall")
        )
    )

    row1[3].metric(
        "Put Wall",
        format_strike(
            liquidity.get("put_wall")
        )
    )

    st.divider()

    # ======================================================
    # Order Imbalance
    # ======================================================

    st.markdown("#### Order Imbalance")

    imbalance = liquidity.get("order_imbalance", {})

    row2 = st.columns(3)

    row2[0].metric(
        "Market Pressure",
        pressure(
            imbalance.get("pressure")
        )
    )

    row2[1].metric(
        "OI Ratio",
        format_ratio(
            imbalance.get("oi_ratio")
        )
    )

    row2[2].metric(
        "Volume Ratio",
        format_ratio(
            imbalance.get("volume_ratio")
        )
    )

    st.divider()

    # ======================================================
    # Liquidity Voids
    # ======================================================

    st.markdown("#### Liquidity Voids")

    voids = liquidity.get("voids", {})

    row3 = st.columns(2)

    row3[0].metric(
        "Void Count",
        voids.get("void_count", "-")
    )

    levels = voids.get("void_levels", [])

    if levels:

        st.dataframe(
            levels,
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    # ======================================================
    # Absorption
    # ======================================================

    st.markdown("#### Absorption")

    absorption = liquidity.get("absorption", {})

    row4 = st.columns(2)

    row4[0].metric(
        "Absorption Count",
        absorption.get("count", "-")
    )

    absorb_levels = absorption.get("levels", [])

    if absorb_levels:

        st.dataframe(
            absorb_levels,
            use_container_width=True,
            hide_index=True
        )