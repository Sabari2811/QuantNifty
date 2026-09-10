from __future__ import annotations

from dashboard.ui_data_contract import build_ui_data_contract


def build_ui_runtime_contract(dashboard) -> dict:
    """Capture every canonical backend value handed to the Streamlit UI.

    The legacy top-level keys remain for compatibility with existing tests and
    consumers. The exhaustive ``sections`` mapping is the authoritative audit
    surface for backend -> UI coverage and integrity checks.
    """
    contract = build_ui_data_contract(dashboard)

    return {
        "market_summary": contract["market_summary"],
        "decision": contract["decision"],
        "intelligence": dashboard.intelligence,
        "decision_intelligence_consistency": dashboard.decision_intelligence_consistency,
        "option_chain": dashboard.option_chain,
        "greeks": dashboard.greeks,
        "provenance": dashboard.data_provenance,
        "option_chain_integrity": dashboard.option_chain_integrity,
        "execution_intent": dashboard.execution_intent,
        "execution_result": dashboard.execution_result,
        "execution_lifecycle": dashboard.execution_lifecycle,
        "position_recovery": dashboard.position_recovery,
        "position_reconciliation": dashboard.position_reconciliation,
        "sections": contract,
    }
