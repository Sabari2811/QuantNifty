from datetime import datetime
from zoneinfo import ZoneInfo

from dashboard.live_validation_worker import is_nse_derivatives_session_open


IST = ZoneInfo("Asia/Kolkata")


def test_live_validation_session_window():
    assert is_nse_derivatives_session_open(datetime(2026, 9, 7, 9, 15, tzinfo=IST))
    assert is_nse_derivatives_session_open(datetime(2026, 9, 7, 15, 40, tzinfo=IST))
    assert not is_nse_derivatives_session_open(datetime(2026, 9, 7, 9, 14, 59, tzinfo=IST))
    assert not is_nse_derivatives_session_open(datetime(2026, 9, 7, 15, 40, 1, tzinfo=IST))


def test_live_validation_skips_weekends():
    saturday = datetime(2026, 9, 12, 10, 0, tzinfo=IST)
    assert not is_nse_derivatives_session_open(saturday)
