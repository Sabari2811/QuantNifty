from datetime import datetime
from zoneinfo import ZoneInfo

from dashboard.live_validation_worker import is_nse_derivatives_session_open


IST = ZoneInfo("Asia/Kolkata")


def test_live_validation_worker_session_boundary_is_inclusive():
    assert is_nse_derivatives_session_open(datetime(2026, 9, 7, 9, 15, tzinfo=IST))
    assert is_nse_derivatives_session_open(datetime(2026, 9, 7, 15, 40, tzinfo=IST))


def test_live_validation_worker_rejects_outside_session_and_weekends():
    assert not is_nse_derivatives_session_open(datetime(2026, 9, 7, 9, 14, tzinfo=IST))
    assert not is_nse_derivatives_session_open(datetime(2026, 9, 7, 15, 41, tzinfo=IST))
    assert not is_nse_derivatives_session_open(datetime(2026, 9, 6, 11, 0, tzinfo=IST))
