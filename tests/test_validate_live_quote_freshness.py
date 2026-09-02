from datetime import datetime, timedelta, timezone

from providers.indmoney_websocket import LiveQuoteTick
from providers.indmoney_websocket import assess_quote_freshness
from tools.validate_live_quote_freshness import validate_consecutive_quotes


def test_runner_requires_positive_cycles_and_timeout():
    try:
        validate_consecutive_quotes("token", "NIDX:40000001", cycles=0)
    except ValueError as exc:
        assert str(exc) == "cycles must be >= 1"
    else:
        raise AssertionError("expected cycles validation")


def test_runner_freshness_gate_semantics(monkeypatch):
    base = datetime(2026, 9, 2, 5, 0, tzinfo=timezone.utc)
    ticks = [
        LiveQuoteTick(
            "40000001",
            base + timedelta(seconds=index),
            1000 + index * 1000,
            "ltp",
            {"ltp": 23880 + index},
        )
        for index in range(3)
    ]

    class FakeFeed:
        def __init__(self, access_token, *, timeout):
            self.ticks = iter(ticks)

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def subscribe(self, instruments, *, mode):
            assert instruments == ["NIDX:40000001"]
            assert mode == "ltp"

        def recv_tick(self):
            return next(self.ticks)

    observed = iter(
        [
            base + timedelta(seconds=1),
            base + timedelta(seconds=1, milliseconds=100),
            base + timedelta(seconds=2, milliseconds=100),
            base + timedelta(seconds=3, milliseconds=100),
        ]
    )

    import tools.validate_live_quote_freshness as module

    monkeypatch.setattr(module, "IndmoneyPriceFeed", FakeFeed)
    monkeypatch.setattr(module, "datetime", type("Clock", (), {
        "now": staticmethod(lambda tz=None: next(observed)),
    }))

    observations, checks = module.validate_consecutive_quotes(
        "token", "NIDX:40000001", cycles=3, max_age_ms=2000
    )

    expected = [
        assess_quote_freshness(tick, received_at=base + timedelta(seconds=offset))
        for tick, offset in zip(ticks, (1.1, 2.1, 3.1))
    ]
    assert [item["freshness_status"] for item in observations] == [item.status for item in expected]
    assert checks["all_cycles_received"] is True
    assert checks["all_quotes_fresh_or_bounded_skew"] is True
    assert checks["no_excessive_clock_skew"] is True
    assert checks["provider_timestamps_monotonic"] is True
