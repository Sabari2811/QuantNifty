import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st

from config.settings import PROVIDER
from dashboard.dashboard_controller import DashboardController
from dashboard.ui_runtime_contract import build_ui_runtime_contract
from dashboard.ui_data_contract import build_ui_integrity_report
from dashboard.components import institutional_score_card
from dashboard.components import intelligence_card
from dashboard.components.brain_performance import render as render_brain_performance
from dashboard.components.backend_ui_integrity import render as render_backend_ui_integrity
from dashboard.components.execution_state import render as render_execution_state
from dashboard.components.trade_cockpit import render as render_trade_cockpit

from dashboard.components import (
    header, market_banner, market_regime, runtime_card, signal_card,
    probability_gauge, expected_move_card, max_pain_card, pcr_card,
    dealer_card, dealer_flow_card, market_structure_card, liquidity_card,
    trade_plan, risk_card, gamma_heatmap, oi_heatmap, option_chain,
    greeks_table, charts,
)

st.set_page_config(page_title="QuantNifty Terminal", page_icon="📈", layout="wide")


@st.cache_resource
def get_controller():
    return DashboardController()


controller = get_controller()

with st.sidebar:
    st.title("⚙ QuantNifty")
    st.success(f"Provider : {PROVIDER.upper()}")
    # QuantNifty's canonical trading engine is NIFTY-specific.
    symbol = st.selectbox("Index", ["NIFTY"])
    levels = st.slider("Strike Levels", min_value=2, max_value=10, value=5)

try:
    dashboard = controller.load(symbol, levels)
except Exception as e:
    message = str(e)
    if "403" in message or "401" in message or "authentication" in message.lower():
        st.error("INDstocks authentication failed. Refresh the current INDstocks access token configured in Render, then redeploy.")
        st.info("The application will not synthesize market data. After the token is refreshed, reload this page to resume live validation.")
    elif "Unable to fetch live quote" in message:
        st.error("Live market quote is currently unavailable. No synthetic market value is being used.")
        st.info("Check the INDstocks live-data connection and reload the application.")
    else:
        st.error("QuantNifty could not build the current live dashboard cycle.")
        st.info("The failure is isolated from the UI mapping layer; inspect the live-data/provider status before counting this cycle as valid live evidence.")
    with st.expander("Technical status", expanded=False):
        st.write(f"Runtime error type: {type(e).__name__}")
    st.stop()

ui_contract = build_ui_runtime_contract(dashboard)
integrity_report = build_ui_integrity_report(dashboard)
st.session_state["_quantnifty_dashboard_audit"] = dashboard
st.session_state["_quantnifty_ui_contract"] = ui_contract
st.session_state["_quantnifty_backend_ui_integrity"] = integrity_report

decision = ui_contract["decision"]
summary = ui_contract["market_summary"]

header.render(dashboard)

main_tab, terminal_tab = st.tabs(["🎯 NIFTY Trade Cockpit", "📊 Full Terminal"])

with main_tab:
    render_trade_cockpit(dashboard)

with terminal_tab:
    # Existing terminal intentionally preserved in full, except the live
    # monitor which is now owned exclusively by the primary cockpit.
    row = st.columns([1.25, 1.25, 1.25], gap="small")
    with row[0]:
        market_banner.render(dashboard)
    with row[1]:
        market_regime.render(dashboard)
    with row[2]:
        intelligence_card.render(dashboard.intelligence, dashboard.decision_intelligence_consistency)

    row = st.columns([1.15, 1.15, 1.7], gap="small")
    with row[0]:
        signal_card.render(decision, dashboard.dealer)
    with row[1]:
        institutional_score_card.render(dashboard.institutional_score)
    with row[2]:
        expected_move_card.render(dashboard.expected_move)

    with st.container(border=True):
        probability_gauge.render(dashboard.probability)

    row = st.columns([1.05, 1.25, 1.25, 1.25], gap="small")
    with row[0]:
        max_pain_card.render(dashboard.max_pain)
    with row[1]:
        pcr_card.render(dashboard.pcr)
    with row[2]:
        market_structure_card.render(dashboard.market_structure)
    with row[3]:
        runtime_card.render(dashboard)

    row = st.columns([1.0, 1.0], gap="small")
    with row[0]:
        dealer_card.render(dashboard.dealer)
    with row[1]:
        dealer_flow_card.render(dashboard.dealer_flow)

    with st.container(border=True):
        liquidity_card.render(dashboard.liquidity)

    with st.container(border=True):
        trade_plan.render(dashboard.trade_plan, decision)

    with st.container(border=True):
        risk_card.render(dashboard.risk)

    with st.container(border=True):
        charts.render(dashboard)

    with st.container(border=True):
        option_chain.render(
            dashboard.option_chain,
            dashboard.greeks,
            dashboard.data_provenance,
            dashboard.option_chain_integrity,
        )

    with st.container(border=True):
        greeks_table.render(dashboard.greeks)

    row = st.columns(2, gap="small")
    with row[0]:
        gamma_heatmap.render(dashboard.greeks)
    with row[1]:
        oi_heatmap.render(dashboard.option_chain)

    with st.expander("⚡ Execution & Position State", expanded=False):
        render_execution_state(ui_contract["sections"])

    with st.expander("🧠 Brain / Paper Performance", expanded=True):
        render_brain_performance(dashboard)

    with st.expander("🔗 Backend ↔ UI Integrity", expanded=True):
        render_backend_ui_integrity(integrity_report)

    with st.expander("📦 Analytics Output"):
        st.json(dashboard.analytics)
