from types import SimpleNamespace

import pandas as pd

from dashboard.live_reconciliation import build_live_reconciliation


def _dashboard():
    return SimpleNamespace(
        spot=24334.55,
        expiry="09/01/2026 14:00",
        expected_move={"atm_strike": 24350, "expected_move": 228.4, "lower": 24106.15, "upper": 24562.95},
        pcr={"oi_pcr": 0.97},
        max_pain={"max_pain": 24200},
        signal={"signal": "WAIT"},
        probability={"bullish_probability": 40, "bearish_probability": 35, "confidence": 52, "reasons": ()},
        trade_plan={"signal": "WAIT"},
        intelligence={"recommendation": "WAIT"},
        option_chain=pd.DataFrame([{
            "Strike": 24350, "CE_ID": 46999, "PE_ID": 47000,
            "CE_LTP": 100.0, "PE_LTP": 100.0,
        }]),
        greeks=pd.DataFrame([{
            "Strike": 24350, "CE_ID": 46999, "PE_ID": 47000,
            "CE_IV": 0.1, "CE_DELTA": 0.5,
        }]),
        data_provenance=None,
    )


def test_option_chain_ui_projection_preserves_canonical_values():
    report = build_live_reconciliation(_dashboard())
    projection = report["option_chain"]["ui_projection"]
    assert projection["status"] == "MATCH"
    assert projection["rows"] == 1
    assert projection["gap"] is None


def test_option_chain_ui_projection_detects_missing_greek_contract():
    dashboard = _dashboard()
    dashboard.greeks = pd.DataFrame(columns=["Strike", "CE_ID", "PE_ID", "CE_IV"])
    report = build_live_reconciliation(dashboard)
    assert report["option_chain"]["ui_projection"]["status"] == "GAP"
    assert "option_chain.contract_identity" in report["gaps"]


def test_option_chain_ui_projection_detects_row_duplication():
    dashboard = _dashboard()
    dashboard.option_chain = pd.concat([dashboard.option_chain, dashboard.option_chain], ignore_index=True)
    dashboard.option_chain.loc[1, "Strike"] = 24400
    dashboard.option_chain.loc[1, "CE_ID"] = 47001
    dashboard.option_chain.loc[1, "PE_ID"] = 47002
    report = build_live_reconciliation(dashboard)
    assert report["option_chain"]["ui_projection"]["status"] == "GAP"
    assert "option_chain.ui_projection" in report["gaps"]
