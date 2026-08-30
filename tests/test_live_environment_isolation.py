from types import SimpleNamespace

from engine.market_data_pipeline import MarketDataPipeline


def test_ws_environment_does_not_activate_for_non_indmoney_provider(monkeypatch):
    monkeypatch.setenv("INDSTOCKS_ENABLE_WS_LIVE_QUOTES", "1")
    monkeypatch.setenv("INDSTOCKS_API_TOKEN", "api-token")
    monkeypatch.setenv("INDSTOCKS_WS_NIFTY_TOKEN", "ws-index-token")

    provider = SimpleNamespace(token="token")
    pipeline = MarketDataPipeline(provider, None, None, None, None)

    assert pipeline.live_feed is None


def test_rest_mode_remains_default_without_ws_flag(monkeypatch):
    monkeypatch.delenv("INDSTOCKS_ENABLE_WS_LIVE_QUOTES", raising=False)
    provider = SimpleNamespace(token="token")

    pipeline = MarketDataPipeline(provider, None, None, None, None)

    assert pipeline.live_feed is None
