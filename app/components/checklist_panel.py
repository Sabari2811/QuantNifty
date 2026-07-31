import streamlit as st


def _status(value):

    value = str(value).upper()

    # Bullish
    if value in [
        "LONG",
        "ABOVE",
        "BULLISH",
        "STRONGLY BULLISH",
        "YES",
        "TRUE"
    ]:
        return "🟢"

    # Bearish
    if value in [
        "SHORT",
        "BELOW",
        "BEARISH",
        "STRONGLY BEARISH",
        "NO",
        "FALSE"
    ]:
        return "🔴"

    # Neutral
    if value in [
        "NEUTRAL",
        "AT_VWAP",
        "AT_EMA",
        "AT_FLIP",
        "UNKNOWN"
    ]:
        return "🟡"

    return "⚪"


def _row(label, value):

    col1, col2 = st.columns([2, 1])

    with col1:
        st.write(f"{_status(value)} **{label}**")

    with col2:
        st.write(value)


def show(ctx):

    snapshot = ctx.snapshot

    if snapshot is None:
        return

    analytics = snapshot.analytics

    dealer = snapshot.dealer

    pcr = snapshot.pcr

    # ----------------------------------------
    # Technical Analysis
    # ----------------------------------------

    technical = analytics.get("technical", {})

    ema = technical.get("ema", {})

    vwap = technical.get("vwap", {})

    st.subheader("✅ Checklist")

    with st.container(border=True):

        # Dealer
        _row(
            "Dealer",
            dealer.get(
                "dealer_gamma",
                "-"
            )
        )

        # Gamma Flip
        gamma_flip = dealer.get("gamma_flip")
        spot = snapshot.spot

        if gamma_flip is None:
            gamma_status = "-"
        else:
            gamma_status = (
                "ABOVE"
                if spot >= gamma_flip
                else "BELOW"
            )

        _row(
            "Gamma Flip",
            gamma_status
        )

        # EMA20
        ema_status = ema.get(
            "status",
            "-"
        )

        _row(
            "EMA20",
            ema_status
        )

        # VWAP
        vwap_status = vwap.get(
            "status",
            "-"
        )

        _row(
            "VWAP",
            vwap_status
        )

        # PCR
        pcr_status = pcr.get(
            "bias",
            "-"
        )

        _row(
            "PCR",
            pcr_status
        )