from datetime import datetime

from decision.nifty_policy import IST, NiftyPolicy


def test_nifty_policy_keeps_entry_and_force_exit_cutoffs_distinct():
    policy = NiftyPolicy()
    assert policy.entry_cutoff.strftime("%H:%M") == "15:35"
    assert policy.force_exit_cutoff.strftime("%H:%M") == "15:35"
    metadata = policy.metadata()
    assert metadata["entry_cutoff_ist"] == "15:35"
    assert metadata["force_exit_cutoff_ist"] == "15:35"


def test_nifty_policy_force_exit_is_explicit_and_weekday_only():
    policy = NiftyPolicy()
    before = datetime(2026, 9, 11, 15, 34, tzinfo=IST)
    cutoff = datetime(2026, 9, 11, 15, 35, tzinfo=IST)
    weekend = datetime(2026, 9, 12, 15, 35, tzinfo=IST)
    assert policy.force_exit_due(before) is False
    assert policy.force_exit_due(cutoff) is True
    assert policy.force_exit_due(weekend) is False
