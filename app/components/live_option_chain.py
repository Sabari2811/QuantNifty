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
        return "🟡 Gamma Flip"

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


def _format_numeric_value(value, decimals=None, thousands=False):
    """Format a numeric scalar for dataframe rendering."""
    if pd.isna(value):
        return "—"

    number = float(value)

    if decimals is not None:
        return f"{number:,.{decimals}f}" if thousands else f"{number:.{decimals}f}"

    if number.is_integer():
        return f"{number:,.0f}" if thousands else f"{number:.0f}"

    return f"{number:g}"


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
# TABLE PREPARATION
# ==========================================================

def _sort_option_chain(display):
    """Keep the live chain in a stable, high-to-low strike order."""
    return (
        display.sort_values("Strike", ascending=False, kind="stable")
        .reset_index(drop=True)
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
# ROW STYLING
# ==========================================================

def _highlight_rows(row, atm):
    """Apply high-contrast semantic row colors without hiding the values."""
    level = row["Level"]

    if "Gamma Flip" in level or "Max Pain" in level:
        background = "#FFF1A8"
        foreground = "#111827"
    elif "Call Wall" in level:
        background = "#F4C7CC"
        foreground = "#111827"
    elif "Put Wall" in level:
        background = "#CDEFD6"
        foreground = "#111827"
    elif row["Strike"] == atm:
        background = "#FFF1A8"
        foreground = "#111827"
    else:
        return ["color:#F8FAFC"] * len(row)

    weight = "700" if row["Strike"] == atm else "600"
    return [
        f"background-color:{background};color:{foreground};font-weight:{weight}"
    ] * len(row)


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
    display_thousands = {}

    numeric_columns = (
        ("CE_LTP", "CE LTP", 2, False),
        ("CE_OI", "CE OI", None, True),
        ("CE_VOLUME", "CE Volume", None, True),
        ("CE_IV", "CE IV", 4, False),
        ("CE_DELTA", "CE Δ", 2, False),
        ("CE_GAMMA", "CE Γ", 4, False),
        ("CE_THETA", "CE Θ", 4, False),
        ("CE_VEGA", "CE Vega", 4, False),
        ("CE_RHO", "CE Rho", 4, False),
        ("PE_GAMMA", "PE Γ", 4, False),
        ("PE_DELTA", "PE Δ", 2, False),
        ("PE_THETA", "PE Θ", 4, False),
        ("PE_VEGA", "PE Vega", 4, False),
        ("PE_RHO", "PE Rho", 4, False),
        ("PE_IV", "PE IV", 4, False),
        ("PE_VOLUME", "PE Volume", None, True),
        ("PE_OI", "PE OI", None, True),
        ("PE_LTP", "PE LTP", 2, False),
    )

    for source, column, decimals, thousands in numeric_columns:
        display[column] = _display_series(df[source], decimals)
        display_decimals[column] = decimals
        display_thousands[column] = thousands

    display["Strike"] = pd.to_numeric(df["Strike"], errors="coerce")
    display["Level"] = display["Strike"].apply(
        lambda x: _get_level(x, analytics)
    )

    # Always present strikes high -> low.  Highlighting never changes row order.
    display = _sort_option_chain(display)
    atm = _find_atm(display, ctx.spot)

    formatter = {
        column: (
            lambda value, decimals=decimals, thousands=display_thousands[column]:
            _format_numeric_value(value, decimals, thousands)
        )
        for column, decimals in display_decimals.items()
    }
    formatter["Strike"] = lambda value: _format_numeric_value(value, thousands=True)

    styled = (
        display.style
        .format(formatter=formatter)
        .set_properties(**{
            "font-size": "14px",
            "padding": "9px 8px",
            "vertical-align": "middle",
        })
        .set_table_styles([
            {
                "selector": "th",
                "props": [
                    ("font-size", "13px"),
                    ("font-weight", "700"),
                    ("padding", "10px 8px"),
                    ("white-space", "nowrap"),
                ],
            },
        ])
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
        height=500,
        row_height=38,
    )

    # Compact semantic legend and the active ordering rule stay inside this component.
    st.markdown(
        """
        <div style="display:flex;gap:10px;align-items:stretch;flex-wrap:wrap;margin-top:8px;">
          <div style="padding:10px 14px;border:1px solid rgba(255,255,255,.10);border-radius:8px;background:rgba(205,239,214,.08);min-width:150px;">
            <div style="font-weight:700;color:#CDEFD6;">🟢 Put Wall</div>
            <div style="font-size:12px;opacity:.75;">Strong support</div>
          </div>
          <div style="padding:10px 14px;border:1px solid rgba(255,255,255,.10);border-radius:8px;background:rgba(255,241,168,.08);min-width:150px;">
            <div style="font-weight:700;color:#FFF1A8;">🟡 Gamma Flip / Max Pain</div>
            <div style="font-size:12px;opacity:.75;">Key gamma / equilibrium level</div>
          </div>
          <div style="padding:10px 14px;border:1px solid rgba(255,255,255,.10);border-radius:8px;background:rgba(244,199,204,.08);min-width:150px;">
            <div style="font-weight:700;color:#F4C7CC;">🔴 Call Wall</div>
            <div style="font-size:12px;opacity:.75;">Strong resistance</div>
          </div>
          <div style="flex:1;min-width:260px;padding:10px 14px;border:1px solid rgba(255,255,255,.10);border-radius:8px;background:rgba(255,255,255,.03);">
            <div style="font-weight:700;">ℹ️ Current view: Strike — High → Low</div>
            <div style="font-size:12px;opacity:.75;">Rows are sorted by strike value; semantic highlighting never changes the order.</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
