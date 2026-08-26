from datetime import datetime

import pandas as pd

from engine.instrument_manager import InstrumentManager


def _rows(*rows):
    return pd.DataFrame(
        rows,
        columns=["TRADING_SYMBOL", "EXPIRY_DATE", "EXPIRY_FLAG"],
    )


def _future_date(days: int) -> str:
    return (pd.Timestamp.now() + pd.Timedelta(days=days)).strftime("%m/%d/%Y %H:%M")


def test_nifty_prefers_nearest_future_weekly_expiry():
    manager = object.__new__(InstrumentManager)
    df = _rows(
        ("NIFTY-OPT", _future_date(7), "W"),
        ("NIFTY-OPT", _future_date(2), "W"),
        ("NIFTY-OPT", _future_date(30), "M"),
    )

    selected = manager._nearest_future_expiry(df, "NIFTY")

    assert selected == df.iloc[1]["EXPIRY_DATE"]


def test_nifty_does_not_silently_fallback_to_monthly_when_weekly_missing(monkeypatch):
    manager = object.__new__(InstrumentManager)
    manager.cache = {}

    monthly_only = _rows(
        ("NIFTY-OPT", _future_date(30), "M"),
    )
    manager.get_options = lambda symbol: monthly_only

    refresh_calls = []

    def refresh(source):
        refresh_calls.append(source)

    manager.download_instruments = refresh

    selected = manager.get_nearest_weekly_expiry("NIFTY")

    assert selected is None
    assert refresh_calls == ["fno"]


def test_nifty_refreshes_stale_master_and_selects_new_weekly_expiry():
    manager = object.__new__(InstrumentManager)
    manager.cache = {}

    stale = _rows(
        ("NIFTY-OPT", _future_date(30), "M"),
    )
    fresh = _rows(
        ("NIFTY-OPT", _future_date(6), "W"),
        ("NIFTY-OPT", _future_date(13), "W"),
        ("NIFTY-OPT", _future_date(30), "M"),
    )

    current = {"df": stale}
    manager.get_options = lambda symbol: current["df"]

    refresh_calls = []

    def refresh(source):
        refresh_calls.append(source)
        current["df"] = fresh

    manager.download_instruments = refresh

    selected = manager.get_nearest_weekly_expiry("NIFTY")

    assert selected == fresh.iloc[0]["EXPIRY_DATE"]
    assert refresh_calls == ["fno"]
