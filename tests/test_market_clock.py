from datetime import datetime

from runtime.market_clock import IST, MarketClock


class _FrozenMarketClock(MarketClock):
    def __init__(self, timestamp):
        self._timestamp = timestamp

    def now(self):
        return self._timestamp


def _clock(local_time):
    return _FrozenMarketClock(
        datetime.fromisoformat(f"2026-09-11T{local_time}+05:30").astimezone(IST)
    )


def test_overnight_is_closed_not_pre_market():
    assert _clock("01:05:00").market_status() == "CLOSED"


def test_pre_open_window_is_pre_market():
    assert _clock("09:00:00").market_status() == "PRE_MARKET"
    assert _clock("09:14:59").market_status() == "PRE_MARKET"


def test_regular_session_boundaries_are_open():
    assert _clock("09:15:00").market_status() == "OPEN"
    assert _clock("15:40:00").market_status() == "OPEN"


def test_after_close_is_closed():
    assert _clock("15:40:01").market_status() == "CLOSED"
