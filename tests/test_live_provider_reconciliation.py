from types import SimpleNamespace

import pandas as pd

from dashboard.live_provider_reconciliation import (
    compare_decision_intelligence_runtime,
    compare_raw_quotes_to_option_chain,
)


def _chain():
    return pd.DataFrame([
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
    ])


def _quotes():
    return {
        "NFO_101": {"live_price": 150.0, "open_interest": 1000, "volume": 100},
        "NFO_102": {"live_price": 140.0, "open_interest": 1200, "volume": 200},
    }


def test_raw_provider_values_match_canonical_option_chain():
    report = compare_raw_quotes_to_option_chain(_quotes(), _chain())

    assert report["status"] == "PASS"
    assert len(report["checks"]) == 6
    assert report["gaps"] == []


def test_raw_provider_mismatch_is_explicit():
    quotes = _quotes()
    quotes["NFO_102"]["volume"] = 999

    report = compare_raw_quotes_to_option_chain(quotes, _chain())

    assert report["status"] == "GAP"
    assert "row0.PE_VOLUME:NFO_102" in report["gaps"]


def test_missing_provider_contract_is_explicit():
    quotes = {"NFO_101": _quotes()["NFO_101"]}

    report = compare_raw_quotes_to_option_chain(quotes, _chain())

    assert report["status"] == "GAP"
    assert "row0.PE_LTP:NFO_102" in report["gaps"]
    assert "row0.PE_OI:NFO_102" in report["gaps"]
    assert "row0.PE_VOLUME:NFO_102" in report["gaps"]


def _decision(signal):
    return SimpleNamespace(signal=SimpleNamespace(name=signal))


def _intelligence(recommendation, direction):
    return SimpleNamespace(
        recommendation=recommendation,
        direction=direction,
    )


def test_live_decision_intelligence_consistency_is_consistent():
    ctx = SimpleNamespace(
        decision=_decision("BUY CALL"),
        intelligence=_intelligence("BUY CALL", "BULLISH"),
    )

    report = compare_decision_intelligence_runtime(ctx)

    assert report["status"] == "CONSISTENT"
    assert report["semantic_status"] == "CONSISTENT"
    assert report["consistent"] is True
    assert report["actionable"] is True


def test_live_decision_intelligence_deferred_state_is_explicit():
    ctx = SimpleNamespace(
        decision=_decision("BUY CALL"),
        intelligence=_intelligence("WAIT", "BULLISH"),
    )

    report = compare_decision_intelligence_runtime(ctx)

    assert report["status"] == "CONFLICT"
    assert report["semantic_status"] == "DEFERRED"
    assert report["consistent"] is False
    assert report["actionable"] is False
    assert report["vetoed"] is True
