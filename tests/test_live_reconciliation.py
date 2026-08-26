from types import SimpleNamespace

import pandas as pd

from dashboard.live_reconciliation import build_live_reconciliation


def _dashboard():
    chain = pd.DataFrame(
        [
            {"Strike": 24350, "CE_ID": 46999, "PE_ID": 47000, "CE_LTP": 100.0, "PE_LTP": 100.0}
        ]
    )
    greeks = pd.DataFrame(
        [
            {"Strike": 24350, "CE_ID": 46999, "PE_ID": 47000, "CE_IV": 0.1}
        ]
    )
    return SimpleNamespace(
        spot=24334.55,
        expiry="09/01/2026 14:00",
        expected_move={
            "atm_strike": 24350,
            "expected_move": 228.4,
            "lower": 24106.15,
            "upper": 24562.95,
        },
        pcr={"oi_pcr": 0.97},
        max_pain={"max_pain": 24200},
        signal={"signal": "WAIT"},
        probability={
            "bullish_probability": 40,
            "bearish_probability": 35,
            "confidence": 52,
            "reasons": (),
        },
        trade_plan={"signal": "WAIT"},
        intelligence={"recommendation": "WAIT"},
        option_chain=chain,
        greeks=greeks,
        data_provenance=None,
    )


def test_live_reconciliation_reports_zero_field_gaps_for_canonical_mapping():
    report = build_live_reconciliation(_dashboard())
    assert report["field_status"] == "MATCH"
    assert report["gaps"] == ()
    assert report["option_chain"]["contract_identity"]["gap"] is None


def test_live_reconciliation_detects_contract_identity_gap():
    dashboard = _dashboard()
    dashboard.greeks = dashboard.greeks.iloc[0:0]

    report = build_live_reconciliation(dashboard)

    assert report["field_status"] == "GAP"
    assert "option_chain.contract_identity" in report["gaps"]
    assert report["option_chain"]["contract_identity"]["gap"]["missing_greek_contracts"]
