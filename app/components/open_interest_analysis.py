import streamlit as st
import pandas as pd

from app.utils.formatters import (
    format_number,
    format_ratio,
    format_strike,
    format_percent,
)

from app.utils.badges import (
    pressure,
)


# ==========================================================
# Component
# ==========================================================

def show(ctx):

    liquidity = ctx.analytics.get("liquidity", {})
    oi = liquidity.get("order_imbalance", {})

    st.header("📊 Open Interest Analysis")

    # ------------------------------------------------------
    # Market Positioning
    # ------------------------------------------------------

    st.subheader("Market Positioning")

    c1, c2, c3 = st.columns(3)

    call_oi = oi.get("call_oi", 0)
    put_oi = oi.get("put_oi", 0)
    oi_ratio = oi.get("oi_ratio", 0)

    c1.metric(
        "Call OI",
        format_number(call_oi)
    )

    c2.metric(
        "Put OI",
        format_number(put_oi)
    )

    c3.metric(
        "OI Ratio",
        format_ratio(oi_ratio)
    )

    st.divider()

    # ------------------------------------------------------
    # Volume Positioning
    # ------------------------------------------------------

    st.subheader("Volume Positioning")

    c1, c2, c3 = st.columns(3)

    call_volume = oi.get("call_volume", 0)
    put_volume = oi.get("put_volume", 0)
    volume_ratio = oi.get("volume_ratio", 0)

    c1.metric(
        "Call Volume",
        format_number(call_volume)
    )

    c2.metric(
        "Put Volume",
        format_number(put_volume)
    )

    c3.metric(
        "Volume Ratio",
        format_ratio(volume_ratio)
    )

    st.divider()

    # ------------------------------------------------------
    # Institutional Positioning
    # ------------------------------------------------------

    st.subheader("Institutional Positioning")

    total = call_oi + put_oi

    call_pct = 0
    put_pct = 0

    if total > 0:
        call_pct = (call_oi / total) * 100
        put_pct = (put_oi / total) * 100

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Market Pressure",
        pressure(
            oi.get("pressure")
        )
    )

    c2.metric(
        "Call Dominance",
        format_percent(call_pct, 1)
    )

    c3.metric(
        "Put Dominance",
        format_percent(put_pct, 1)
    )

    st.divider()

    # ------------------------------------------------------
    # Top Call Writing
    # ------------------------------------------------------

    st.subheader("Top Call Writing")

    calls = liquidity.get("top_call_walls", [])

    if calls:

        df = pd.DataFrame(calls)

        df.rename(
            columns={
                "Strike": "Strike",
                "CE_OI": "Call OI"
            },
            inplace=True
        )

        if "Strike" in df.columns:
            df["Strike"] = df["Strike"].apply(format_strike)

        if "Call OI" in df.columns:
            df["Call OI"] = df["Call OI"].apply(format_number)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    # ------------------------------------------------------
    # Top Put Writing
    # ------------------------------------------------------

    st.subheader("Top Put Writing")

    puts = liquidity.get("top_put_walls", [])

    if puts:

        df = pd.DataFrame(puts)

        df.rename(
            columns={
                "Strike": "Strike",
                "PE_OI": "Put OI"
            },
            inplace=True
        )

        if "Strike" in df.columns:
            df["Strike"] = df["Strike"].apply(format_strike)

        if "Put OI" in df.columns:
            df["Put OI"] = df["Put OI"].apply(format_number)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    # ------------------------------------------------------
    # Institutional Interpretation
    # ------------------------------------------------------

    st.subheader("Institutional Interpretation")

    support = liquidity.get("support")
    resistance = liquidity.get("resistance")

    interpretation = []

    if put_oi > call_oi:
        interpretation.append(
            "✅ Put Open Interest exceeds Call Open Interest."
        )
    else:
        interpretation.append(
            "✅ Call Open Interest exceeds Put Open Interest."
        )

    interpretation.append(
        f"📈 Market Pressure : {pressure(oi.get('pressure'))}"
    )

    interpretation.append(
        f"🛡️ Strong Support : {format_strike(support)}"
    )

    interpretation.append(
        f"🚧 Strong Resistance : {format_strike(resistance)}"
    )

    if volume_ratio > 1:
        interpretation.append(
            "📊 Volume confirms institutional participation."
        )

    if oi_ratio > 1:
        interpretation.append(
            "🟢 Bullish OI structure."
        )
    else:
        interpretation.append(
            "🔴 Bearish OI structure."
        )

    st.info("\n\n".join(interpretation))