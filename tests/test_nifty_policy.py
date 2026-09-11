from datetime import datetime

from analytics.market_snapshot.market_snapshot import MarketSnapshot
from decision.nifty_policy import IST, NiftyPolicy


def test_nifty_policy_is_nifty_only():
    policy = NiftyPolicy()
    assert policy.validate_symbol("NIFTY") == (True, "")
    assert policy.validate_symbol("BANKNIFTY")[0] is False


def test_nifty_policy_allows_only_ce_and_pe():
    policy = NiftyPolicy()
    assert policy.validate_option("CE")[0] is True
    assert policy.validate_option("PE")[0] is True
    assert policy.validate_option("FUT")[0] is False


def test_nifty_policy_requires_meaningful_delta():
    policy = NiftyPolicy()
    assert policy.validate_delta(0.40)[0] is True
    assert policy.validate_delta(0.0)[0] is False


def test_nifty_policy_blocks_entries_at_intraday_cutoff():
    policy = NiftyPolicy()
    at_cutoff = datetime(2026, 9, 11, 15, 35, tzinfo=IST)
    assert policy.entry_allowed(at_cutoff) == (False, "NIFTY_INTRADAY_ENTRY_CUTOFF")


def test_nifty_policy_enforces_daily_move_model():
    policy = NiftyPolicy()
    assert policy.validate_daily_move(24000, 24400)[0] is True
    assert policy.validate_daily_move(24000, 24401)[0] is False


def test_nifty_policy_extracts_real_session_open_without_fabrication():
    snapshot = MarketSnapshot().save(
        greeks_df=None,
        spot=24420,
        analytics={"technical": {"session_open": 24000}},
    )
    policy = NiftyPolicy()
    assert policy.session_open_from_snapshot(snapshot) == 24000
    assert policy.validate_snapshot_move(snapshot) == (False, "NIFTY_DAILY_MOVE_BOUND_EXCEEDED:420.00")


def test_nifty_policy_does_not_invent_session_open():
    snapshot = MarketSnapshot().save(greeks_df=None, spot=24420, analytics={})
    assert NiftyPolicy().session_open_from_snapshot(snapshot) is None
    assert NiftyPolicy().validate_snapshot_move(snapshot) == (True, "")
