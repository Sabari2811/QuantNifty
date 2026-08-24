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
# DISPLAY HELPERS
# ==========================================================

def _display_series(series, decimals=None):
    """Return a deterministic UI representation with explicit missing values."""

    values = pd.to_numeric(series, errors="coerce")

    def render(value):
        if pd.isna(value):
            return "—"

        number = float(value)

        if decimals is not None:
            return f"{number:.{decimals}f}"

        if number.is_integer():
            return f"{number:.0f}"

        return f"{number:g}"

    return values.map(render).astype("string")


def _format_missing(value):
    """Render a missing scalar as a visible dash without changing real values."""

    return "—" if pd.isna(value) else value


def _provenance_message(ctx):
    """Return a UI warning when acquisition provenance is incomplete."""

    provenance = getattr(ctx, "data_provenance", None)
    if provenance is None:
        return None

    incomplete = []
    for name in ("option_chain", "spot", "candles"):
        acquisition = getattr(provenance, name, None)
        if acquisition is not None and not acquisition.complete:
            incomplete.append(name.replace("_", " "))

    if not incomplete:
        return None

    return (
        "Live data is incomplete for: "
        + ", ".join(incomplete)
        + ". Missing observations are shown as —; displayed zeroes are "
        "actual zero values, not placeholders."
    )


# ==========================================================
# ATM DETECTION
# ==========================================================

def _find_atm(df, spot):

    return min(
        df["Strike"],
        key=lambda x: abs(x - spot),
    )


# ==========================================================
# ROW COLORING
# ==========================================================

def _highlight_rows(row, atm):

    if row["Strike"] == atm:
        return ["background-color:#FFF3B0;font-weight:bold"] * len(row)

    level = row["Level"]

    if "Gamma Flip" in level:
        return ["background-color:#D4EDDA"] * len(row)

    if "Max Pain" in level:
        return ["background-color:#FFF3B0"] * len(row)

    if "Call Wall" in level:
        return ["background-color:#F8D7DA"] * len(row)

    if "Put Wall" in level:
        return ["background-color:#D4EDDA"] * len(row)

    return [""] * len(row)


# ==========================================================
# UI
# ==========================================================

def show(ctx):

    st.subheader("📊 Live Option Chain")

    provenance_message = _provenance_message(ctx)
    if provenance_message:
        st.warning(provenance_message)

    df = ctx.greeks_df

    if df is None or df.empty:
        st.warning("Option Chain not available.")
        return

    analytics = ctx.analytics or {}

    display = pd.DataFrame()

    display["CE LTP"] = _display_series(df["CE_LTP"])
    display["CE OI"] = _display_series(df["CE_OI"])
    display["CE Volume"] = _display_series(df["CE_VOLUME"])
    display["CE IV"] = _display_series(df["CE_IV"], 4)
    display["CE Δ"] = _display_series(df["CE_DELTA"], 2)
    display["CE Γ"] = _display_series(df["CE_GAMMA"], 4)
    display["CE Θ"] = _display_series(df["CE_THETA"], 4)
    display["CE Vega"] = _display_series(df["CE_VEGA"], 4)
    display["CE Rho"] = _display_series(df["CE_RHO"], 4)

    display["Strike"] = pd.to_numeric(df["Strike"], errors="coerce")

    display["Level"] = display["Strike"].apply(
        lambda x: _get_level(x, analytics)
    )

    display["PE Γ"] = _display_series(df["PE_GAMMA"], 4)
    display["PE Δ"] = _display_series(df["PE_DELTA"], 2)
    display["PE Θ"] = _display_series(df["PE_THETA"], 4)
    display["PE Vega"] = _display_series(df["PE_VEGA"], 4)
    display["PE Rho"] = _display_series(df["PE_RHO"], 4)
    display["PE IV"] = _display_series(df["PE_IV"], 4)
    display["PE Volume"] = _display_series(df["PE_VOLUME"])
    display["PE OI"] = _display_series(df["PE_OI"])
    display["PE LTP"] = _display_series(df["PE_LTP"])

    atm = _find_atm(display, ctx.spot)

    styled = display.style.apply(
        _highlight_rows,
        axis=1,
        atm=atm,
    )

    st.dataframe(
        styled,
        hide_index=True,
        width="stretch",
        height=430,
    )
