import streamlit as st

from app.services.live_service import LiveService

from app.components.hero_header import show as header
from app.components.kpi_cards import show as kpi_cards
from app.components.active_position_card import active_position_card
from app.components.trade_journal_card import trade_journal_card
from app.components.market_map_panel import show as market_map
from app.components.checklist_panel import show as checklist
from app.components.ai_decision_card import show as ai_decision
from app.components.trade_plan_card import show as trade_plan
from app.components.market_intelligence_card import show as market_intelligence
from app.components.live_option_chain import show as live_option_chain
from dashboard.components.intelligence_card import render as intelligence
from dashboard.intelligence_adapter import adapt_intelligence


def show():

    # ==========================================================
    # LOAD LIVE DATA
    # ==========================================================

    service = LiveService()

    ctx = service.get_context()

    # ==========================================================
    # HEADER
    # ==========================================================

    header(ctx)

    # ==========================================================
    # PORTFOLIO KPI
    # ==========================================================

    kpi_cards(ctx)

    st.divider()

    # ==========================================================
    # ACTIVE POSITION
    # ==========================================================

    active_position_card(ctx)

    st.divider()

    # ==========================================================
    # RECENT TRADES
    # ==========================================================

    trade_journal_card(ctx)

    st.divider()

    # ==========================================================
    # ROW 1
    # Market Overview
    # ==========================================================

    left, right = st.columns([2, 1])

    with left:
        market_map(ctx)

    with right:
        checklist(ctx)

    st.divider()

    # ==========================================================
    # ROW 2
    # Decision
    # ==========================================================

    left, right = st.columns([2, 1])

    with left:
        ai_decision(ctx)

    with right:
        trade_plan(ctx)

    st.divider()

    # ==========================================================
    # ROW 3
    # Intelligence
    # ==========================================================

    intelligence(adapt_intelligence(ctx.intelligence))

    st.divider()

    # ==========================================================
    # ROW 4
    # Live Option Chain
    # ==========================================================

    live_option_chain(ctx)
