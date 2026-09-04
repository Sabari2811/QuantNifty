from datetime import datetime, timezone

from providers.indmoney_websocket import LiveQuoteTick
from providers.live_quote_coordinator import LiveQuoteBatch, LiveQuoteCoordinator


def test_live_quote_batch_latest_timestamp():
    first = LiveQuoteTick("NFO:1", datetime(2026, 8, 30, 4, 0, tzinfo=timezone.utc), 1, "quote", {"ltp": 10})
    second = LiveQuoteTick("NFO:2", datetime(2026, 8, 30, 4, 0, 1, tzinfo=timezone.utc), 2, "quote", {"ltp": 20})
    completed = datetime(2026, 8, 30, 4, 0, 2, tzinfo=timezone.utc)
    batch = LiveQuoteBatch(
        ticks={first.instrument: first, second.instrument: second},
        received_at={first.instrument: completed, second.instrument: completed},
        freshness={},
        acquired_at=completed,
        connected_at=completed,
        completed_at=completed,
    )
    assert batch.latest_provider_timestamp == second.timestamp


def test_provider_instrument_without_segment_matches_requested():
    tick = LiveQuoteTick(
        "40000001",
        datetime(2026, 9, 2, 5, 0, tzinfo=timezone.utc),
        1000,
        "ltp",
        {"ltp": 23880},
    )
    assert LiveQuoteCoordinator._matches_requested(tick, {"NIDX:40000001"}) == "NIDX:40000001"


def test_ambiguous_suffix_does_not_match():
    tick = LiveQuoteTick(
        "40000001",
        datetime(2026, 9, 2, 5, 0, tzinfo=timezone.utc),
        1000,
        "ltp",
        {"ltp": 23880},
    )
    assert LiveQuoteCoordinator._matches_requested(
        tick, {"NIDX:40000001", "NFO:40000001"}
    ) is None


def test_websocket_instrument_mapping():
    assert LiveQuoteCoordinator.option_instrument(51011) == "NFO:51011"
    assert LiveQuoteCoordinator.index_instrument(26000) == "NIDX:26000"
