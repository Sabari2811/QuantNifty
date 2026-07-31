import streamlit as st


# ==========================================================
# HELPERS
# ==========================================================

def _find_atm(ctx):

    try:

        df = ctx.greeks_df

        if df is None or df.empty:
            return "-"

        return min(
            df["Strike"],
            key=lambda x: abs(x - ctx.spot)
        )

    except Exception:

        return "-"


def _get_pcr(ctx):

    try:

        pcr = ctx.analytics.get("pcr", {})

        value = pcr.get("oi_pcr")

        if value is None:
            return "-"

        return f"{value:.2f}"

    except Exception:

        return "-"


def _get_max_pain(ctx):

    try:

        mp = ctx.analytics.get("max_pain", {})

        value = mp.get("max_pain")

        if value is None:
            return "-"

        return f"{value:.0f}"

    except Exception:

        return "-"


def _get_expected_move(ctx):

    try:

        em = ctx.analytics.get("expected_move", {})

        low = em.get("lower")
        high = em.get("upper")

        if low is None or high is None:
            return "-"

        return f"{low:.2f} - {high:.2f}"

    except Exception:

        return "-"


def _get_expiry(ctx):

    try:

        return ctx.expiry

    except Exception:

        return "-"


# ==========================================================
# UI
# ==========================================================

def show(ctx):

    st.subheader("📈 Market Summary")

    row1 = st.columns(3)
    row2 = st.columns(3)

    row1[0].metric(
        "Spot",
        f"{ctx.spot:,.2f}"
    )

    row1[1].metric(
        "ATM Strike",
        _find_atm(ctx)
    )

    row1[2].metric(
        "PCR",
        _get_pcr(ctx)
    )

    row2[0].metric(
        "Max Pain",
        _get_max_pain(ctx)
    )

    row2[1].metric(
        "Expected Move",
        _get_expected_move(ctx)
    )

    row2[2].metric(
        "Expiry",
        _get_expiry(ctx)
    )