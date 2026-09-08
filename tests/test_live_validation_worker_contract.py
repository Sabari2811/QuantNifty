from datetime import datetime
from zoneinfo import ZoneInfo

from dashboard.live_validation_worker import (
    DEFAULT_INTERVAL_SECONDS,
    MIN_INTERVAL_SECONDS,
    get_validation_interval_seconds,
    is_nse_derivatives_session_open,
)


IST = ZoneInfo("Asia/Kolkata")


def test_live_validation_worker_session_boundary_is_inclusive():
    assert is_nse_derivatives_session_open(datetime(2026, 9, 7, 9, 15, tzinfo=IST))
    assert is_nse_derivatives_session_open(datetime(2026, 9, 7, 15, 40, tzinfo=IST))


def test_live_validation_worker_rejects_outside_session_and_weekends():
    assert not is_nse_derivatives_session_open(datetime(2026, 9, 7, 9, 14, tzinfo=IST))
    assert not is_nse_derivatives_session_open(datetime(2026, 9, 7, 15, 41, tzinfo=IST))
    assert not is_nse_derivatives_session_open(datetime(2026, 9, 6, 11, 0, tzinfo=IST))


def test_live_validation_worker_uses_safe_interval_defaults_and_clamps():
    assert get_validation_interval_seconds(None) == DEFAULT_INTERVAL_SECONDS
    assert get_validation_interval_seconds(60) == 60
    assert get_validation_interval_seconds("not-a-number") == DEFAULT_INTERVAL_SECONDS
    assert get_validation_interval_seconds(1) == MIN_INTERVAL_SECONDS
    assert get_validation_interval_seconds(0) == MIN_INTERVAL_SECONDS
