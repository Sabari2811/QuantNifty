from types import SimpleNamespace

import pandas as pd

from dashboard.components.intelligence_card import _render_consistency
from dashboard.live_reconciliation import build_live_reconciliation
from dashboard.live_provider_reconciliation import compare_dashboard_ui_runtime


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

    return SimpleNamespace(
        symbol="NIFTY",
        spot=25020.0,
        expiry="09/08/2026 14:00",
        trade_status="BLOCKED",
        trade_block_reason="",
        runtime_status="IDLE",
        cycle_no=1,
        option_chain=option_chain,
        greeks=greeks,
        data_provenance=SimpleNamespace(),
        option_chain_integrity=None,
        dealer=SimpleNamespace(
            dealer_gamma=None,
            market_mode=None,
            support=None,
            resistance=None,
            gamma_flip=None,
            gamma_wall=None,
            expected_volatility=None,
            mean_reversion_probability=None,
            breakout_probability=None,
            total_gex=None,
        ),
        dealer_flow={},
        expected_move={"atm_strike": 25000, "expected_move": 290.0, "lower": 24730.0, "upper": 25310.0, "method": "ATM_STRADDLE"},
        max_pain={"max_pain": 25000, "call_oi": 1000, "put_oi": 1200, "total_oi": 2200},
        pcr={"oi_pcr": 1.2, "volume_pcr": 2.0},
        market_structure={},
        liquidity={},
        probability={"bullish_probability": 60.0, "bearish_probability": 40.0, "confidence": 60.0, "reasons": ("r",)},
        signal={"signal": "BUY CALL"},
        trade_plan={"signal": "BUY CALL"},
        risk={},
        institutional_score={},
        analytics={},
        canonical_intelligence=None,
        intelligence=None,
        decision_intelligence_consistency={},
    )


def test_live_reconciliation_matches_market_summary_and_detects_no_mapping_gaps():
    dashboard = _dashboard()
    report = build_live_reconciliation(dashboard)
    assert report["field_status"] == "MATCH"
    assert "market_summary.pcr" not in report["gaps"]
    assert report["market_summary"]["pcr"]["backend"] == 1.2
    assert report["market_summary"]["pcr"]["ui"] == 1.2
    assert "decision_intelligence" not in report["gaps"]


def test_live_reconciliation_can_match_option_projection_with_authoritative_columns():
    dashboard = _dashboard()
    report = build_live_reconciliation(dashboard)
    assert report["option_chain"]["contract_identity"]["option_chain_unique"] is True
    assert report["option_chain"]["contract_identity"]["greeks_unique"] is True


def test_intelligence_card_has_explicit_direction_consistency_ui_path():
    source = open("dashboard/components/intelligence_card.py", encoding="utf-8").read()
    assert "def _render_consistency(consistency):" in source
    assert "Semantic status:" in source
    assert "Actionable:" in source
    assert "Vetoed:" in source


def test_dashboard_ui_runtime_report_exposes_field_level_decision_checks():
    dashboard = _dashboard()
    report = compare_dashboard_ui_runtime(dashboard)

    assert report["decision"]["status"] == "PASS"
    assert all(item["status"] == "PASS" for item in report["decision"]["fields"].values())
    assert report["decision"]["fields"]["signal"]["backend"] == "BUY CALL"
    assert report["decision"]["fields"]["signal"]["ui"] == "BUY CALL"
