import os
import sys

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st

from config.settings import PROVIDER
from dashboard.dashboard_controller import DashboardController
from dashboard.components import institutional_score_card
from dashboard.components import intelligence_card

from dashboard.components import (
    header,
    market_banner,
    market_regime,
    runtime_card,
    signal_card,
    probability_gauge,
    expected_move_card,
    max_pain_card,
    pcr_card,
    dealer_card,
    dealer_flow_card,
    market_structure_card,
    liquidity_card,
    trade_plan,
    risk_card,
    gamma_heatmap,
    oi_heatmap,
    option_chain,
    greeks_table,
    charts,
)

st.set_page_config(
    page_title="QuantNifty Terminal",
    page_icon="📈",
    layout="wide",
)


@st.cache_resource
def get_controller():
    return DashboardController()


controller = get_controller()

with st.sidebar:
    st.title("⚙ QuantNifty")
    st.success(f"Provider : {PROVIDER.upper()}")
    symbol = st.selectbox(
        "Index",
        [
            "NIFTY",
            "BANKNIFTY",
            "FINNIFTY",
        ],
    )
    levels = st.slider(
        "Strike Levels",
        min_value=2,
        max_value=10,
        value=5,
    )

try:
    dashboard = controller.load(symbol, levels)
except Exception as e:
    st.exception(e)
    st.stop()

header.render(dashboard)
market_banner.render(dashboard)
market_regime.render(dashboard)
runtime_card.render(dashboard)

intelligence_card.render(dashboard.intelligence)
signal_card.render(dashboard.probability, dashboard.dealer)
institutional_score_card.render(dashboard.institutional_score)
probability_gauge.render(dashboard.probability)
expected_move_card.render(dashboard.expected_move)
max_pain_card.render(dashboard.max_pain)
pcr_card.render(dashboard.pcr)
market_structure_card.render(dashboard.market_structure)
dealer_card.render(dashboard.dealer)
dealer_flow_card.render(dashboard.dealer_flow)
liquidity_card.render(dashboard.liquidity)
trade_plan.render(dashboard.trade_plan, dashboard.signal)
risk_card.render(dashboard.risk)
gamma_heatmap.render(dashboard.greeks)
oi_heatmap.render(dashboard.option_chain)

# Live option-chain view must use Greeks and provenance from the same canonical runtime cycle.
option_chain.render(
    dashboard.option_chain,
    dashboard.greeks,
    dashboard.data_provenance,
)

greeks_table.render(dashboard.greeks)
charts.render(dashboard)

with st.expander("📦 Analytics Output"):
    st.json(dashboard.analytics)
