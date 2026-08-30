from datetime import datetime, timedelta, timezone

from engine.market_data_pipeline import MarketDataPipeline


def test_recent_candle_is_fresh():
    now = datetime.now(timezone.utc)
    verified, age, status, reasons = MarketDataPipeline._candle_freshness(
        now - timedelta(minutes=2), now
    )
    assert verified is True
    assert age is not None and age < 180
    assert status == "FRESH"
    assert reasons == ("provider_candle_timestamp",)


def test_old_candle_is_stale_not_verified():
    now = datetime.now(timezone.utc)
    verified, age, status, reasons = MarketDataPipeline._candle_freshness(
        now - timedelta(hours=45), now
    )
    assert verified is False
    assert age is not None and age > 44 * 3600
    assert status == "STALE"
    assert "provider_candle_stale" in reasons


def test_future_candle_timestamp_is_unverified():
    now = datetime.now(timezone.utc)
    verified, age, status, reasons = MarketDataPipeline._candle_freshness(
        now + timedelta(minutes=1), now
    )
    assert verified is False
    assert age is None
    assert status == "UNVERIFIED"
    assert reasons == ("provider_candle_timestamp_in_future",)
