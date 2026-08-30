from types import SimpleNamespace

import pytest

from engine.market_data_pipeline import MarketDataPipeline


def test_ws_live_feed_requires_explicit_index_token(monkeypatch):
    monkeypatch.setenv("INDSTOCKS_ENABLE_WS_LIVE_QUOTES", "1")
    monkeypatch.delenv("INDSTOCKS_WS_NIFTY_TOKEN", raising=False)
    provider = SimpleNamespace(token="token")
    with pytest.raises(RuntimeError, match="INDSTOCKS_WS_NIFTY_TOKEN"):
        MarketDataPipeline(provider, None, None, None, None)


def test_rest_mode_remains_default(monkeypatch):
    monkeypatch.delenv("INDSTOCKS_ENABLE_WS_LIVE_QUOTES", raising=False)
    provider = SimpleNamespace(token="token")
    pipeline = MarketDataPipeline(provider, None, None, None, None)
    assert pipeline.live_feed is None
