from __future__ import annotations

from dashboard.decision_adapter import adapt_decision
from dashboard.market_summary_adapter import adapt_market_summary


def build_ui_runtime_contract(dashboard) -> dict:
    """Capture the exact canonical values handed to the affected UI sections.

    This is an audit surface for Streamlit runtime tests. It intentionally does
    not recompute backend analytics: each value is taken from the DashboardData
    object and from the same adapters used by the app entrypoint.
    """
    summary = adapt_market_summary(dashboard)
    decision = adapt_decision(dashboard)

    return {
        "market_summary": summary,
        "decision": decision,
        "intelligence": dashboard.intelligence,
        "decision_intelligence_consistency": dashboard.decision_intelligence_consistency,
        "option_chain": dashboard.option_chain,
        "greeks": dashboard.greeks,
        "provenance": dashboard.data_provenance,
        "option_chain_integrity": dashboard.option_chain_integrity,
    }
