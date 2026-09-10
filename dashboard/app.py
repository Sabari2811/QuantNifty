import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st

from config.settings import PROVIDER
from dashboard.dashboard_controller import DashboardController
from dashboard.market_summary_adapter import adapt_market_summary
from dashboard.decision_adapter import adapt_decision
from dashboard.ui_runtime_contract import build_ui_runtime_contract
from dashboard.ui_data_contract import build_ui_integrity_report
from dashboard.components import institutional_score_card
from dashboard.components import intelligence_card
from dashboard.components.brain_performance import render as render_brain_performance
from dashboard.components.backend_ui_integrity import render as render_backend_ui_integrity
from dashboard.components.execution_state import render as render_execution_state
from dashboard.live_validation_worker import start_live_validation_worker

from dashboard.components import (
    header, market_banner, market_regime, runtime_card, signal_card,
    probability_gauge, expected_move_card, max_pain_card, pcr_card,
    dealer_card, dealer_flow_card, market_structure_card, liquidity_card,
    trade_plan, risk_card, gamma_heatmap, oi_heatmap, option_chain,
    greeks_table, charts,
)

st.set_page_config(page_title="QuantNifty Terminal", page_icon="📈", layout="wide")

if os.getenv("RENDER_LIVE_WORKER", "").strip().lower() == "true":
    start_live_validation_worker()


@st.cache_resource
def get_controller():
    return DashboardController()


controller = get_controller()

with st.sidebar:
    st.title("⚙ QuantNifty")
    st.success(f"Provider : {PROVIDER.upper()}")
    symbol = st.selectbox("Index", ["NIFTY", "BANKNIFTY", "FINNIFTY"])
    levels = st.slider("Strike Levels", min_value=2, max_value=10, value=5)

try:
    dashboard = controller.load(symbol, levels)
except Exception as e:
    st.exception(e)
    st.stop()

# Build the backend -> UI contract once. All affected UI sections are sourced
# from this same canonical DashboardData cycle; no component should recompute
# analytics independently.
ui_contract = build_ui_runtime_contract(dashboard)
integrity_report = build_ui_integrity_report(dashboard)
st.session_state["_quantnifty_dashboard_audit"] = dashboard
st.session_state["_quantnifty_ui_contract"] = ui_contract
st.session_state["_quantnifty_backend_ui_integrity"] = integrity_report

decision = ui_contract["decision"]
summary = ui_contract["market_summary"]

header.render(dashboard)
market_banner.render(dashboard)
market_regime.render(dashboard)
runtime_card.render(dashboard)
intelligence_card.render(dashboard.intelligence, dashboard.decision_intelligence_consistency)
signal_card.render(decision, dashboard.dealer)
institutional_score_card.render(dashboard.institutional_score)
probability_gauge.render(dashboard.probability)

expected_move_card.render({
    "spot": summary["spot"],
    "expected_move": summary["expected_move"],
    "upper": summary["expected_move_upper"],
    "lower": summary["expected_move_lower"],
    "method": summary["expected_move_method"],
})

max_pain_card.render(dashboard.max_pain)
pcr_card.render(dashboard.pcr)
market_structure_card.render(dashboard.market_structure)
dealer_card.render(dashboard.dealer)
dealer_flow_card.render(dashboard.dealer_flow)
liquidity_card.render(dashboard.liquidity)
trade_plan.render(dashboard.trade_plan, decision)
risk_card.render(dashboard.risk)
gamma_heatmap.render(dashboard.greeks)
oi_heatmap.render(dashboard.option_chain)
option_chain.render(dashboard.option_chain, dashboard.greeks, dashboard.data_provenance, dashboard.option_chain_integrity)
greeks_table.render(dashboard.greeks)
charts.render(dashboard)

with st.expander("🔗 Backend ↔ UI Integrity", expanded=True):
    render_backend_ui_integrity(integrity_report)

with st.expander("⚡ Execution & Position State", expanded=False):
    render_execution_state(ui_contract["sections"])

with st.expander("🧠 Brain / Paper Performance", expanded=True):
    render_brain_performance()

with st.expander("📦 Analytics Output"):
    st.json(dashboard.analytics)
