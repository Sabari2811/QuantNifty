from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from providers.indmoney_websocket import LiveQuoteTick
from providers.live_quote_coordinator import LiveQuoteCoordinator
from engine.market_data_pipeline import MarketDataPipeline


def test_candle_cache_skips_historical_fetch_within_refresh_window(monkeypatch):
    pipeline = object.__new__(MarketDataPipeline)
    calls = []
    pipeline._fetch_spot = lambda ctx: calls.append("spot")
    pipeline._fetch_option_chain = lambda ctx: calls.append("chain")
    pipeline._fetch_historical_candles = lambda ctx: calls.append("candles")
    now = datetime.now(timezone.utc)
    ctx = SimpleNamespace(
        candles=object(),
        candles_acquired_at=now,
        data_provenance=SimpleNamespace(spot="spot", option_chain="chain", candles="candles"),
    )

    pipeline._run_live(ctx)

    assert calls == ["spot", "chain"]


def test_candle_cache_refreshes_after_window(monkeypatch):
    pipeline = object.__new__(MarketDataPipeline)
    calls = []
    pipeline._fetch_spot = lambda ctx: calls.append("spot")
    pipeline._fetch_option_chain = lambda ctx: calls.append("chain")
    pipeline._fetch_historical_candles = lambda ctx: calls.append("candles")
    ctx = SimpleNamespace(
        candles=object(),
        candles_acquired_at=datetime.now(timezone.utc) - timedelta(seconds=61),
        data_provenance=SimpleNamespace(spot="spot", option_chain="chain", candles="candles"),
    )

    pipeline._run_live(ctx)

    assert calls == ["spot", "chain", "candles"]


def test_websocket_coordinator_reuses_connection(monkeypatch):
    class FakeFeed:
        connects = 0
        closes = 0

        def __init__(self, access_token, timeout):
            self.access_token = access_token
            self.timeout = timeout
            self.calls = 0

        def connect(self):
            type(self).connects += 1

        def subscribe(self, instruments, mode):
            self.instruments = list(instruments)
            self.mode = mode

        def recv_tick(self, timeout):
            self.calls += 1
            return LiveQuoteTick(
                instrument="26000",
                timestamp=datetime.now(timezone.utc),
                timestamp_ms=int(datetime.now(timezone.utc).timestamp() * 1000),
                mode="quote",
                data={"ltp": 25000},
            )

        def close(self):
            type(self).closes += 1

    monkeypatch.setattr("providers.live_quote_coordinator.IndmoneyPriceFeed", FakeFeed)
    coordinator = LiveQuoteCoordinator("test-token", timeout=1)

    first = coordinator.collect(["NIDX:26000"])
    second = coordinator.collect(["NIDX:26000"])

    assert first.ticks
    assert second.ticks
    assert FakeFeed.connects == 1

    coordinator.close()
    assert FakeFeed.closes == 1
