import streamlit as st


# ==========================================================
# HELPERS
# ==========================================================

def _institutional(ctx):
    try:
        return (
            ctx.analytics
            .get("institutional_score", {})
            .get("institutional", {})
        )
    except Exception:
        return {}


def _score(ctx):

    try:

        inst = _institutional(ctx)

        score = inst.get("score", "-")
        max_score = inst.get("max_score", 100)

        if score == "-":
            return "-"

        return f"{score} / {max_score}"

    except Exception:

        return "-"


def _grade(ctx):

    try:
        return _institutional(ctx).get("grade", "-")
    except Exception:
        return "-"


def _strength(ctx):

    try:
        return _institutional(ctx).get("strength", "-")
    except Exception:
        return "-"


def _recommendation(ctx):

    try:
        return _institutional(ctx).get("signal", "-")
    except Exception:
        return "-"


# ==========================================================
# UI
# ==========================================================

def show(ctx):

    st.subheader("🏦 Institutional Summary")

    row1 = st.columns(2)
    row2 = st.columns(2)

    row1[0].metric(
        "Institutional Score",
        _score(ctx)
    )

    row1[1].metric(
        "Grade",
        _grade(ctx)
    )

    row2[0].metric(
        "Strength",
        _strength(ctx)
    )

    row2[1].metric(
        "Recommendation",
        _recommendation(ctx)
    )

    # ==========================================================
    # DEBUG (Temporary)
    # ==========================================================

    st.divider()

    with st.expander("🔍 Analytics Debug"):

        st.write("Dealer")
        st.json(ctx.analytics.get("dealer", {}))

        st.write("Institutional Score")
        st.json(ctx.analytics.get("institutional_score", {}))

        st.write("Signal")
        st.json(ctx.analytics.get("signal", {}))

        st.write("Dealer Flow")
        st.json(ctx.analytics.get("dealer_flow", {}))

        st.write("Probability")
        st.json(ctx.analytics.get("probability", {}))

        # NEW
        st.write("Liquidity")
        st.json(ctx.analytics.get("liquidity", {}))

        st.write("Volatility")
        st.json(ctx.analytics.get("volatility", {}))