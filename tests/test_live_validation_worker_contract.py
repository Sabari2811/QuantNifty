from datetime import datetime
from zoneinfo import ZoneInfo

from dashboard.live_validation_worker import (
    DEFAULT_INTERVAL_SECONDS,
    MIN_INTERVAL_SECONDS,
    _persistence_status,
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


def test_live_validation_worker_requires_both_persistence_stores_for_durable_status():
    durable_brain = type("Brain", (), {"_sql_store": object()})()
    durable_evidence = type("Evidence", (), {"durable": True})()
    local_evidence = type("Evidence", (), {"durable": False})()

    assert _persistence_status(durable_evidence, durable_brain) == "DURABLE_DATABASE"
    assert _persistence_status(local_evidence, durable_brain) == "LOCAL_OR_PARTIAL"

    local_brain = type("Brain", (), {"_sql_store": None})()
    assert _persistence_status(durable_evidence, local_brain) == "LOCAL_OR_PARTIAL"
