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
    """Keep the transport/display Series numeric; preserve missing data as NA."""

    values = pd.to_numeric(series, errors="coerce")

    if decimals is not None:
        values = values.round(decimals)

    return values


def _format_series_value(value, decimals=None):
    """Format a numeric scalar for the visible option-chain table."""

    if pd.isna(value):
        return "—"

    number = float(value)

    if decimals is not None:
        return f"{number:.{decimals}f}"

    if number.is_integer():
        return f"{number:.0f}"

    return f"{number:g}"


def _format_numeric_value(value, decimals=None):
    """Format a numeric scalar for dataframe rendering."""

    return _format_series_value(value, decimals)


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
    display_decimals = {}

    numeric_columns = (
        ("CE_LTP", "CE LTP", None),
        ("CE_OI", "CE OI", None),
        ("CE_VOLUME", "CE Volume", None),
        ("CE_IV", "CE IV", 4),
        ("CE_DELTA", "CE Δ", 2),
        ("CE_GAMMA", "CE Γ", 4),
        ("CE_THETA", "CE Θ", 4),
        ("CE_VEGA", "CE Vega", 4),
        ("CE_RHO", "CE Rho", 4),
        ("PE_GAMMA", "PE Γ", 4),
        ("PE_DELTA", "PE Δ", 2),
        ("PE_THETA", "PE Θ", 4),
        ("PE_VEGA", "PE Vega", 4),
        ("PE_RHO", "PE Rho", 4),
        ("PE_IV", "PE IV", 4),
        ("PE_VOLUME", "PE Volume", None),
        ("PE_OI", "PE OI", None),
        ("PE_LTP", "PE LTP", None),
    )

    for source, column, decimals in numeric_columns:
        display[column] = _display_series(df[source], decimals)
        display_decimals[column] = decimals

    display["Strike"] = pd.to_numeric(df["Strike"], errors="coerce")

    display["Level"] = display["Strike"].apply(
        lambda x: _get_level(x, analytics)
    )

    atm = _find_atm(display, ctx.spot)

    formatter = {
        column: (
            lambda value, decimals=decimals:
            _format_numeric_value(value, decimals)
        )
        for column, decimals in display_decimals.items()
    }
    formatter["Strike"] = lambda value: _format_numeric_value(value)

    styled = (
        display.style
        .format(formatter=formatter)
        .apply(
            _highlight_rows,
            axis=1,
            atm=atm,
        )
    )

    st.dataframe(
        styled,
        hide_index=True,
        width="stretch",
        height=430,
    )
