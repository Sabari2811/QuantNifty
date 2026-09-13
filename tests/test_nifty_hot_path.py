from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from core.data_provenance import AcquisitionProvenance, RuntimeDataProvenance
from engine.nifty_hot_path_engine import NiftyHotPathEngine


def _provenance(provider_timestamp):
    return AcquisitionProvenance(
        source="test",
        acquired_at=provider_timestamp,
        provider_timestamp=provider_timestamp,
        expected_count=1,
        received_count=1,
        missing_count=0,
        freshness_verified=True,
        freshness_seconds=0.0,
        reasons=("provider_candle_timestamp",),
    )


def test_hot_path_reuses_recent_candles_without_rest_call():
    now = datetime.now(timezone.utc)
    engine = NiftyHotPathEngine.__new__(NiftyHotPathEngine)
    engine._cached_candles = [{"close": 1}]
    engine._cached_candle_at = now - timedelta(seconds=10)
    engine._cached_candle_provenance = _provenance(now - timedelta(seconds=20))
    engine.market_pipeline = SimpleNamespace(
        CANDLE_FRESH_SECONDS=300,
        CANDLE_AGING_SECONDS=900,
        _fetch_historical_candles=lambda ctx: (_ for _ in ()).throw(AssertionError("REST candle fetch must not run")),
    )
    ctx = SimpleNamespace(
        candles=None,
        data_provenance=RuntimeDataProvenance(
            spot=_provenance(now),
            option_chain=_provenance(now),
        ),
    )

    engine._refresh_candles_if_needed(ctx)

    assert ctx.candles == [{"close": 1}]
    assert ctx.data_provenance.candles.freshness_verified is True


def test_hot_path_refreshes_candles_after_cache_interval():
    now = datetime.now(timezone.utc)
    calls = []
    engine = NiftyHotPathEngine.__new__(NiftyHotPathEngine)
    engine._cached_candles = [{"close": 1}]
    engine._cached_candle_at = now - timedelta(seconds=61)
    engine._cached_candle_provenance = _provenance(now - timedelta(seconds=20))

    def fetch(ctx):
        calls.append(True)
        ctx.candles = [{"close": 2}]
        ctx.data_provenance = RuntimeDataProvenance(
            spot=_provenance(now),
            option_chain=_provenance(now),
            candles=_provenance(now),
        )

    engine.market_pipeline = SimpleNamespace(
        CANDLE_FRESH_SECONDS=300,
        CANDLE_AGING_SECONDS=900,
        _fetch_historical_candles=fetch,
    )
    ctx = SimpleNamespace(candles=None, data_provenance=RuntimeDataProvenance(spot=_provenance(now), option_chain=_provenance(now)))

    engine._refresh_candles_if_needed(ctx)

    assert calls == [True]
    assert ctx.candles == [{"close": 2}]
