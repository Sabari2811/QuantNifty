from types import SimpleNamespace

import pandas as pd

from dashboard.live_raw_analytics_reconciliation import reconcile_raw_quote_analytics


def _chain():
    return pd.DataFrame([
        {"Strike": 25000, "CE_ID": 101, "PE_ID": 102},
        {"Strike": 25100, "CE_ID": 103, "PE_ID": 104},
    ])


def _quotes():
    return {
        "NFO_101": {"live_price": 150.0, "open_interest": 1000, "volume": 100},
        "NFO_102": {"live_price": 140.0, "open_interest": 1200, "volume": 200},
        "NFO_103": {"live_price": 100.0, "open_interest": 500, "volume": 50},
        "NFO_104": {"live_price": 160.0, "open_interest": 800, "volume": 100},
    }


def _analytics():
    return {
        "pcr": {
            "oi_pcr": 1.33,
            "volume_pcr": 2.0,
            "call_oi": 1500,
            "put_oi": 2000,
            "call_volume": 150,
            "put_volume": 300,
        },
        "expected_move": {
            "atm_strike": 25000,
            "expected_move": 290.0,
            "upper": 25290.0,
            "lower": 24710.0,
            "method": "ATM_STRADDLE",
        },
        "max_pain": {
            "max_pain": 25000,
            "call_oi": 1000,
            "put_oi": 1200,
            "total_oi": 2200,
        },
    }


def test_raw_quote_analytics_match_canonical_outputs():
    report = reconcile_raw_quote_analytics(_quotes(), _chain(), 25020.0, _analytics())
    assert report["status"] == "PASS"
    assert report["validated_fields"] == 15
    assert report["gaps"] == []


def test_raw_quote_analytics_mismatch_is_explicit():
    analytics = _analytics()
    analytics["pcr"]["oi_pcr"] = 9.99
    report = reconcile_raw_quote_analytics(_quotes(), _chain(), 25020.0, analytics)
    assert report["status"] == "GAP"
    assert "pcr.oi_pcr" in report["gaps"]


def test_missing_provider_contract_is_explicit():
    quotes = _quotes()
    del quotes["NFO_104"]
    report = reconcile_raw_quote_analytics(quotes, _chain(), 25020.0, _analytics())
    assert report["status"] == "GAP"
    assert "provider_contract_missing:25100" in report["gaps"]
