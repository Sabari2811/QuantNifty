import pandas as pd
import pytest

from post_market.strategy_lab import STRATEGIES, run_post_market_replay


def _sample():
    ts = pd.date_range("2026-09-15 03:45:00+00:00", periods=50, freq="min")
    rows = []
    for i, stamp in enumerate(ts):
        spot = 23100 + i * 2
        rows.append({
            "timestamp": stamp,
            "underlying": "NIFTY",
            "spot": spot,
            "option_type": "CE",
            "strike": round(spot / 50) * 50,
            "expiry": "2026-09-15",
            "option_ltp": max(20.0, 50 + i * 0.5),
            "volume": 1000,
        })
        rows.append({
            "timestamp": stamp,
            "underlying": "NIFTY",
            "spot": spot,
            "option_type": "PE",
            "strike": round(spot / 50) * 50,
            "expiry": "2026-09-15",
            "option_ltp": max(20.0, 50 - i * 0.2),
            "volume": 1000,
        })
    return pd.DataFrame(rows)


def test_contract_is_nifty_only_and_exposes_all_strategy_families():
    result = run_post_market_replay(_sample())
    assert result["contract"]["underlying"] == "NIFTY"
    assert result["contract"]["max_trades_per_day"] == 3
    assert {row["strategy"] for row in result["strategies"]} == set(STRATEGIES)


def test_non_nifty_data_fails_closed():
    frame = _sample()
    frame["underlying"] = "BANKNIFTY"
    with pytest.raises(ValueError, match="NIFTY-only"):
        run_post_market_replay(frame)
