from datetime import datetime

from runtime.market_clock import MarketClock, IST


class FixedClock(MarketClock):
    def __init__(self, value):
        self.value = value

    def now(self):
        return self.value


def _clock(hour, minute, weekday=0):
    # 2026-09-07 is Monday; offset keeps weekday deterministic.
    day = 7 + weekday
    return FixedClock(datetime(2026, 9, day, hour, minute, tzinfo=IST))


def test_market_clock_uses_nse_derivatives_close_1540():
    assert MarketClock.MARKET_OPEN.isoformat() == "09:15:00"
    assert MarketClock.MARKET_CLOSE.isoformat() == "15:40:00"

    assert _clock(15, 40).is_market_open() is True
    assert _clock(15, 41).is_market_open() is False


def test_market_clock_rejects_weekends():
    clock = FixedClock(datetime(2026, 9, 12, 11, 0, tzinfo=IST))  # Saturday

    assert clock.is_weekday() is False
    assert clock.is_market_open() is False
    assert clock.market_status() == "CLOSED"
    assert clock.is_post_market() is True


def test_market_clock_classifies_pre_and_post_market():
    assert _clock(9, 14).market_status() == "PRE_MARKET"
    assert _clock(9, 15).market_status() == "OPEN"
    assert _clock(15, 40).market_status() == "OPEN"
    assert _clock(15, 41).market_status() == "CLOSED"
