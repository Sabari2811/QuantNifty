from types import SimpleNamespace

import pandas as pd
import pytest

from models.dashboard_data import DashboardData
from models.dealer_data import DealerData


pytest.importorskip("streamlit.testing.v1")
from streamlit.testing.v1 import AppTest


def _dashboard():
    option_chain = pd.DataFrame(
        [
            {
                "Strike": 25000,
                "CE_ID": 101,
                "CE_LTP": 150.0,
                "CE_OI": 1000,
                "CE_VOLUME": 100,
                "PE_ID": 102,
                "PE_LTP": 140.0,
                "PE_OI": 1200,
                "PE_VOLUME": 200,
            }
        ]
    )
    greeks = option_chain.copy()
    greeks["CE_IV"] = 20.0
    greeks["CE_DELTA"] = 0.5
    greeks["CE_GAMMA"] = 0.01
    greeks["CE_THETA"] = -1.0
    greeks["CE_VEGA"] = 2.0
    greeks["CE_RHO"] = 1.0
    greeks["PE_IV"] = 21.0
    greeks["PE_DELTA"] = -0.5
    greeks["PE_GAMMA"] = 0.01
    greeks["PE_THETA"] = -1.0
    greeks["PE_VEGA"] = 2.0
    greeks["PE_RHO"] = -1.0

    return DashboardData(
        provider="indmoney",
        symbol="NIFTY",
        spot=25020.0,
        expiry="09/08/2026 14:00",
        dealer=DealerData(
            dealer_gamma="POSITIVE",
            market_mode="RANGE",
            support=None,
            resistance=None,
            gamma_flip=None,
            gamma_wall=None,
            expected_volatility="NORMAL",
            mean_reversion_probability=0.5,
            breakout_probability=0.5,
            total_gex=0.0,
        ),
        dealer_flow={},
        expected_move={
            "atm_strike": 25000,
            "expected_move": 290.0,
            "lower": 24730.0,
            "upper": 25310.0,
            "method": "ATM_STRADDLE",
        },
        max_pain={"max_pain": 25000, "call_oi": 1000, "put_oi": 1200, "total_oi": 2200},
        pcr={"oi_pcr": 1.2, "volume_pcr": 2.0},
        market_structure={},
        liquidity={},
        probability={
            "bullish_probability": 60.0,
            "bearish_probability": 40.0,
            "confidence": 60.0,
            "reasons": ("r",),
        },
        signal={"signal": "BUY CALL"},
        trade_plan={"signal": "BUY CALL"},
        risk={},
        institutional_score={},
        analytics={},
        option_chain=option_chain,
        greeks=greeks,
        data_provenance=SimpleNamespace(source="test-provider"),
        option_chain_integrity={"status": "PASS"},
        intelligence={"recommendation": "BUY CALL", "direction": "BULLISH"},
        canonical_intelligence=SimpleNamespace(),
        decision_intelligence_consistency={
            "status": "MATCH",
            "semantic_status": "CONSISTENT",
            "consistent": True,
            "actionable": True,
            "vetoed": False,
            "decision_signal": "BUY CALL",
        },
        trade_status="BLOCKED",
        trade_block_reason="",
        runtime_status="IDLE",
        cycle_no=1,
    )


def test_streamlit_entrypoint_exposes_exact_runtime_ui_contract(monkeypatch):
    dashboard = _dashboard()

    from dashboard.dashboard_controller import DashboardController

    monkeypatch.setattr(
        DashboardController,
        "load",
        lambda self, symbol, levels: dashboard,
    )

    # The contract test targets the real Streamlit entrypoint/orchestration.
    # Component internals are separately covered by their own tests; replacing
    # their render functions keeps this test deterministic and focused on the
    # values handed to the UI boundary.
    component_modules = [
        "header",
        "market_banner",
        "market_regime",
        "runtime_card",
        "signal_card",
        "probability_gauge",
        "expected_move_card",
        "max_pain_card",
        "pcr_card",
        "dealer_card",
        "dealer_flow_card",
        "market_structure_card",
        "liquidity_card",
        "trade_plan",
        "risk_card",
        "gamma_heatmap",
        "oi_heatmap",
        "option_chain",
        "greeks_table",
        "charts",
        "intelligence_card",
        "institutional_score_card",
    ]
    import importlib

    for name in component_modules:
        module = importlib.import_module(f"dashboard.components.{name}")
        monkeypatch.setattr(module, "render", lambda *args, **kwargs: None)

    app = AppTest.from_file("dashboard/app.py")
    app.run()

    assert not app.exception
    contract = app.session_state["_quantnifty_ui_contract"]

    assert contract["decision"] == {
        "signal": "BUY CALL",
        "bullish_probability": 60.0,
        "bearish_probability": 40.0,
        "confidence": 60.0,
        "reasons": ("r",),
        "trade_plan_signal": "BUY CALL",
    }
    assert contract["intelligence"] is dashboard.intelligence
    assert contract["decision_intelligence_consistency"] is dashboard.decision_intelligence_consistency
    assert contract["provenance"] is dashboard.data_provenance
    assert contract["option_chain_integrity"] is dashboard.option_chain_integrity
    pd.testing.assert_frame_equal(contract["option_chain"], dashboard.option_chain)
    pd.testing.assert_frame_equal(contract["greeks"], dashboard.greeks)


def test_streamlit_contract_is_fail_closed_for_missing_provenance():
    dashboard = _dashboard()
    dashboard.data_provenance = None

    from dashboard.ui_runtime_contract import build_ui_runtime_contract

    contract = build_ui_runtime_contract(dashboard)
    assert contract["provenance"] is None
