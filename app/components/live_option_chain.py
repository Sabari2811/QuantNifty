import pandas as pd
import streamlit as st


# ==========================================================
# LEVEL DETECTION
# ==========================================================

def _get_level(strike, analytics):

    dealer = analytics.get("dealer", {})
    max_pain = analytics.get("max_pain", {})

    gamma_flip = dealer.get("gamma_flip")
    call_wall = dealer.get("call_wall")
    put_wall = dealer.get("put_wall")
    max_pain_level = max_pain.get("max_pain")

    if strike == gamma_flip:
        return "🟢 Gamma Flip"

    if strike == max_pain_level:
        return "🟡 Max Pain"

    if strike == call_wall:
        return "🔴 Call Wall"

    if strike == put_wall:
        return "🟢 Put Wall"

    return ""


# ==========================================================
# ATM DETECTION
# ==========================================================

def _find_atm(df, spot):

    return min(

        df["Strike"],

        key=lambda x: abs(x - spot)

    )


# ==========================================================
# ROW COLORING
# ==========================================================

def _highlight_rows(row, atm):

    if row["Strike"] == atm:

        return [

            "background-color:#FFF3B0;font-weight:bold"

        ] * len(row)

    level = row["Level"]

    if "Gamma Flip" in level:

        return [

            "background-color:#D4EDDA"

        ] * len(row)

    if "Max Pain" in level:

        return [

            "background-color:#FFF3B0"

        ] * len(row)

    if "Call Wall" in level:

        return [

            "background-color:#F8D7DA"

        ] * len(row)

    if "Put Wall" in level:

        return [

            "background-color:#D4EDDA"

        ] * len(row)

    return [

        ""

    ] * len(row)


# ==========================================================
# UI
# ==========================================================

def show(ctx):

    st.subheader("📊 Live Option Chain")

    df = ctx.greeks_df

    if df is None or df.empty:

        st.warning(
            "Option Chain not available."
        )

        return

    analytics = ctx.analytics

    display = pd.DataFrame()

    display["CE LTP"] = df["CE_LTP"]

    display["CE OI"] = df["CE_OI"]

    display["CE Δ"] = df["CE_DELTA"].round(2)

    display["CE Γ"] = df["CE_GAMMA"].round(4)

    display["Strike"] = df["Strike"]

    display["Level"] = display["Strike"].apply(

        lambda x: _get_level(

            x,

            analytics

        )

    )

    display["PE Γ"] = df["PE_GAMMA"].round(4)

    display["PE Δ"] = df["PE_DELTA"].round(2)

    display["PE OI"] = df["PE_OI"]

    display["PE LTP"] = df["PE_LTP"]

    atm = _find_atm(

        display,

        ctx.spot

    )

    styled = display.style.apply(

        _highlight_rows,

        axis=1,

        atm=atm

    )

    st.dataframe(

        styled,

        hide_index=True,

        use_container_width=True,

        height=430

    )