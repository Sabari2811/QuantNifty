from types import SimpleNamespace

import pandas as pd

from dashboard.intelligence_adapter import adapt_intelligence
from dashboard.live_reconciliation import build_live_reconciliation


_GREEK_COLUMNS = [
    "CE_IV", "CE_DELTA", "CE_GAMMA", "CE_THETA", "CE_VEGA", "CE_RHO",
    "PE_IV", "PE_DELTA", "PE_GAMMA", "PE_THETA", "PE_VEGA", "PE_RHO",
]


def _canonical_intelligence():
    scenario = SimpleNamespace(
        name="Range",
        direction="NEUTRAL",
        probability=60.0,
        trigger="",
        invalidation="",
        rationale="",
    )
    return SimpleNamespace(
        contract_version="R2-005-A",
        timestamp=None,
        recommendation="WAIT",
        direction="NEUTRAL",
        confidence_before=52.0,
        confidence_after=52.0,
        conviction=40.0,
        opportunity_quality=35.0,
        execution_quality=30.0,
        risk_quality=70.0,
        explanation="",
        regime=SimpleNamespace(
            regime="RANGE",
            previous_regime="UNKNOWN",
            transition=False,
            transition_reason="",
            confidence=55.0,
        ),
        primary_scenario=scenario,
        alternative_scenario=None,
        invalidation=(),
        reasons=(),
        evidence=SimpleNamespace(
            similar_markets=0,
            average_similarity=0.0,
            best_similarity=0.0,
            win_rate=0.0,
            average_pnl=0.0,
            average_holding_minutes=0.0,
            target_probability=0.0,
            stoploss_probability=0.0,
            breakeven_probability=0.0,
            recommendation="WAIT",
            confidence_adjustment=0.0,
            explanation="",
        ),
        evidence_summary=SimpleNamespace(
            bullish_count=0,
            bearish_count=0,
            neutral_count=1,
            independent_count=1,
            correlated_count=0,
            confluence_score=0.0,
            conflict_score=0.0,
        ),
        data_quality=SimpleNamespace(
            score=100.0,
            stale=False,
            incomplete=False,
            invalid=False,
            freshness_verified=False,
            reasons=(),
        ),
    )


def _dashboard():
    chain = pd.DataFrame(
        [{"Strike": 24350, "CE_ID": 46999, "PE_ID": 47000, "CE_LTP": 100.0, "PE_LTP": 100.0}]
    )
    greek_row = {"Strike": 24350, "CE_ID": 46999, "PE_ID": 47000}
    greek_row.update({column: 0.1 for column in _GREEK_COLUMNS})
    canonical_intelligence = _canonical_intelligence()
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
        intelligence=adapt_intelligence(canonical_intelligence),
        canonical_intelligence=canonical_intelligence,
        decision_intelligence_consistency=SimpleNamespace(
            status="CONSISTENT",
            semantic_status="CONSISTENT",
            consistent=True,
            actionable=False,
            vetoed=False,
            decision_signal="WAIT",
            intelligence_recommendation="WAIT",
            intelligence_direction="NEUTRAL",
            reason="Decision is non-actionable; Intelligence does not veto it.",
        ),
        option_chain=chain,
        greeks=pd.DataFrame([greek_row]),
        data_provenance=None,
    )


def test_live_reconciliation_reports_zero_field_gaps_for_canonical_mapping():
    report = build_live_reconciliation(_dashboard())
    assert report["field_status"] == "MATCH"
    assert report["gaps"] == ()
    assert report["intelligence"]["status"] == "MATCH"
    assert report["decision_intelligence"]["status"] == "MATCH"
    assert report["option_chain"]["contract_identity"]["gap"] is None


def test_live_reconciliation_detects_contract_identity_gap():
    dashboard = _dashboard()
    dashboard.greeks = dashboard.greeks.iloc[0:0]

    report = build_live_reconciliation(dashboard)

    assert report["field_status"] == "GAP"
    assert "option_chain.contract_identity" in report["gaps"]
    assert report["option_chain"]["contract_identity"]["gap"]["missing_greek_contracts"]


def test_live_reconciliation_detects_intelligence_adapter_drift():
    dashboard = _dashboard()
    dashboard.intelligence = dict(dashboard.intelligence)
    dashboard.intelligence["recommendation"] = "BUY"

    report = build_live_reconciliation(dashboard)

    assert report["intelligence"]["status"] == "GAP"
    assert report["intelligence"]["gap"] == "ui_intelligence_value_mismatch"
    assert "intelligence" in report["gaps"]
