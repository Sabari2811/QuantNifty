import pandas as pd
import streamlit as st

from core.data_provenance import RuntimeDataProvenance
from dashboard.provenance_adapter import adapt_provenance


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

# These columns are produced by the canonical analytics pipeline and must not
# be dropped at the DashboardData -> UI projection boundary.
_ANALYTICS_COLUMNS = [
    "CE_GEX",
    "PE_GEX",
    "NET_GEX",
    "CE_DEX",
    "PE_DEX",
    "NET_DEX",
    "CE_VANNA",
    "PE_VANNA",
    "NET_VANNA",
    "CE_CHARM",
    "PE_CHARM",
    "NET_CHARM",
    "PREV_CE_LTP",
    "PREV_CE_OI",
    "PREV_PE_LTP",
    "PREV_PE_OI",
    "_PREV_SNAPSHOT_MATCH",
    "CE_PRICE_CHANGE",
    "PE_PRICE_CHANGE",
    "CE_OI_CHANGE",
    "PE_OI_CHANGE",
    "CE_FLOW",
    "PE_FLOW",
]


def _merge_authoritative_greeks(option_chain: pd.DataFrame, greeks: pd.DataFrame | None):
    """Join same-cycle Greeks and analytics without inventing or dropping values."""
    if greeks is None or greeks.empty:
        return option_chain.copy()

    required = {"Strike", "CE_ID", "PE_ID", *_GREEK_COLUMNS}
    if not required.issubset(greeks.columns):
        return option_chain.copy()

    projection_columns = [
        column
        for column in [*_GREEK_COLUMNS, *_ANALYTICS_COLUMNS]
        if column in greeks.columns
    ]
    greek_view = greeks[["Strike", "CE_ID", "PE_ID", *projection_columns]].copy()

    # The Greeks dataframe is authoritative for projected analytics. Remove
    # overlapping UI columns before the identity-safe one-to-one merge so the
    # result has canonical column names rather than *_greeks suffixes.
    overlapping = [column for column in projection_columns if column in option_chain.columns]
    base = option_chain.drop(columns=overlapping, errors="ignore")

    merged = base.merge(
        greek_view,
        on=["Strike", "CE_ID", "PE_ID"],
        how="left",
        validate="one_to_one",
    )
    return merged


def _option_chain_provenance(provenance: RuntimeDataProvenance | None) -> dict | None:
    """Return only the canonical option-chain provenance used by this view."""
    payload = adapt_provenance(provenance)
    return payload.get("option_chain")


def _integrity_findings(integrity: dict | None) -> tuple[str, ...]:
    """Return human-readable contract-specific integrity findings from backend output."""
    if not integrity:
        return ()

    findings = []
    for contract, reasons in integrity.get("contract_reasons", ()):
        reason_text = ", ".join(reasons)
        findings.append(f"{contract}: {reason_text}")
    return tuple(findings)


def _render_provenance(
    provenance: RuntimeDataProvenance | None,
    integrity: dict | None = None,
) -> None:
    """Display independent backend quality states without deriving one from another."""
    state = _option_chain_provenance(provenance)
    if state is None:
        st.warning("Option-chain provenance unavailable")
        return

    coverage = f"{state['received_count']}/{state['expected_count']} ({state['coverage_ratio']:.1f}%)"
    integrity_status = state["integrity_status"]
    freshness = state["freshness_status"]
    source = state["source"] or "Unknown"

    columns = st.columns(4)
    columns[0].metric("Coverage", coverage)
    columns[1].metric("Integrity", integrity_status)
    columns[2].metric("Freshness", freshness)
    columns[3].metric("Source", source)

    details = []
    if state["provider_timestamp"] is not None:
        details.append(f"Provider timestamp: {state['provider_timestamp']}")
    if state["freshness_seconds"] is not None:
        details.append(f"Age: {state['freshness_seconds']:.1f}s")
    if state["missing_count"]:
        details.append(f"Missing contracts: {state['missing_count']}")
    if state["integrity_reasons"]:
        details.append("Integrity: " + ", ".join(state["integrity_reasons"]))
    if state["reasons"]:
        details.append("Data quality: " + ", ".join(state["reasons"]))

    findings = _integrity_findings(integrity)
    if findings:
        with st.expander("View data-quality details"):
            st.write("Affected contracts")
            for finding in findings:
                st.code(finding)

    if details:
        st.caption(" · ".join(details))


def render(df, greeks=None, provenance=None, integrity=None):
    st.subheader("📑 Live Option Chain")

    if df is None or df.empty:
        st.warning("No Option Chain Available")
        return

    _render_provenance(provenance, integrity)
    table = _merge_authoritative_greeks(df, greeks)
    # Provider provenance lives on dataframe.attrs and is rendered separately
    # above. Do not pass non-serializable provenance objects into Streamlit's
    # Arrow/Stylers serialization path.
    table.attrs = {}

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
    st.dataframe(styled, width="stretch", height=420)
