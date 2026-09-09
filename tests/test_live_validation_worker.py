from datetime import datetime
from zoneinfo import ZoneInfo

from dashboard.live_validation_worker import _health_snapshot, get_validation_interval_seconds, is_nse_derivatives_session_open


IST = ZoneInfo("Asia/Kolkata")


def test_live_validation_session_window():
    assert is_nse_derivatives_session_open(datetime(2026, 9, 7, 9, 15, tzinfo=IST))
    assert is_nse_derivatives_session_open(datetime(2026, 9, 7, 15, 40, tzinfo=IST))
    assert not is_nse_derivatives_session_open(datetime(2026, 9, 7, 9, 14, 59, tzinfo=IST))
    assert not is_nse_derivatives_session_open(datetime(2026, 9, 7, 15, 40, 1, tzinfo=IST))


def test_live_validation_skips_weekends():
    saturday = datetime(2026, 9, 12, 10, 0, tzinfo=IST)
    assert not is_nse_derivatives_session_open(saturday)


def test_live_validation_interval_is_fail_safe(monkeypatch):
    monkeypatch.delenv("LIVE_VALIDATION_INTERVAL_SECONDS", raising=False)
    assert get_validation_interval_seconds() == 60
    assert get_validation_interval_seconds("invalid") == 60
    assert get_validation_interval_seconds("2") == 5
    assert get_validation_interval_seconds("15") == 15


def test_live_validation_health_state_is_safe_metadata_only():
    snapshot = _health_snapshot()
    assert snapshot["status"] == "starting"
    assert snapshot["cycles"] == 0
    assert "token" not in snapshot
    assert "APITOKEN" not in snapshot
