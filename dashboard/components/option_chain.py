import pandas as pd
import streamlit as st


_GREEK_COLUMNS = [
    "CE_IV",
    "CE_DELTA",
    "CE_GAMMA",
    "CE_THETA",
    "CE_VEGA",
    "CE_RHO",
    "PE_IV",
    "PE_DELTA",
    "PE_GAMMA",
    "PE_THETA",
    "PE_VEGA",
    "PE_RHO",
]


def _merge_authoritative_greeks(option_chain: pd.DataFrame, greeks: pd.DataFrame | None):
    """Join Greeks from the same runtime cycle without inventing values."""
    if greeks is None or greeks.empty:
        return option_chain.copy()

    required = {"Strike", *["CE_ID", "PE_ID"], *_GREEK_COLUMNS}
    if not required.issubset(greeks.columns):
        return option_chain.copy()

    greek_columns = ["Strike", "CE_ID", "PE_ID", *_GREEK_COLUMNS]
    greek_view = greeks[greek_columns].copy()

    # Contract IDs are the authoritative identity; strike is retained as a
    # deterministic fallback only for legacy/replay frames without stable IDs.
    merged = option_chain.merge(
        greek_view,
        on=["Strike", "CE_ID", "PE_ID"],
        how="left",
        validate="one_to_one",
        suffixes=("", "_greeks"),
    )
    return merged


def render(df, greeks=None):
    st.subheader("📑 Live Option Chain")

    if df is None or df.empty:
        st.warning("No Option Chain Available")
        return

    table = _merge_authoritative_greeks(df, greeks)

    max_ce_oi = table["CE_OI"].max()
    max_pe_oi = table["PE_OI"].max()
    max_ce_vol = table["CE_VOLUME"].max()
    max_pe_vol = table["PE_VOLUME"].max()

    def highlight(row):
        style = [""] * len(row)
        columns = list(table.columns)

        if row["CE_OI"] == max_ce_oi:
            style[columns.index("CE_OI")] = "background-color:#006400;color:white;font-weight:bold"

        if row["PE_OI"] == max_pe_oi:
            style[columns.index("PE_OI")] = "background-color:#8B0000;color:white;font-weight:bold"

        if row["CE_VOLUME"] == max_ce_vol:
            style[columns.index("CE_VOLUME")] = "background-color:#1E90FF;color:white"

        if row["PE_VOLUME"] == max_pe_vol:
            style[columns.index("PE_VOLUME")] = "background-color:#1E90FF;color:white"

        return style

    styled = table.style.apply(highlight, axis=1)

    st.dataframe(
        styled,
        use_container_width=True,
        height=420,
    )
