from datetime import datetime
from zoneinfo import ZoneInfo

from decision.nifty_policy import NiftyPolicy


IST = ZoneInfo("Asia/Kolkata")


def test_nifty_policy_exposes_entry_and_force_exit_cutoffs_separately():
    policy = NiftyPolicy()
    metadata = policy.metadata()

    assert metadata["entry_cutoff_ist"] == "15:35"
    assert metadata["force_exit_cutoff_ist"] == "15:35"
    assert policy.entry_cutoff != policy.force_exit_cutoff or metadata["entry_cutoff_ist"] == metadata["force_exit_cutoff_ist"]


def test_entry_is_blocked_at_cutoff_and_force_exit_is_due():
    policy = NiftyPolicy()
    before = datetime(2026, 9, 14, 15, 34, tzinfo=IST)
    at_cutoff = datetime(2026, 9, 14, 15, 35, tzinfo=IST)

    assert policy.entry_allowed(before)[0] is True
    assert policy.entry_allowed(at_cutoff)[0] is False
    assert policy.force_exit_due(before) is False
    assert policy.force_exit_due(at_cutoff) is True


def test_weekend_never_requests_force_exit():
    policy = NiftyPolicy()
    saturday = datetime(2026, 9, 19, 15, 35, tzinfo=IST)

    assert policy.entry_allowed(saturday)[0] is False
    assert policy.force_exit_due(saturday) is False
