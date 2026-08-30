from types import SimpleNamespace

from engine.market_data_pipeline import MarketDataPipeline


def test_ws_live_feed_requires_real_indmoney_provider(monkeypatch):
    """Production WS wiring applies only to the real INDMoney provider."""
    monkeypatch.setenv("INDSTOCKS_ENABLE_WS_LIVE_QUOTES", "1")
    monkeypatch.setenv("INDSTOCKS_API_TOKEN", "api-token")
    provider = SimpleNamespace(token="token")
    pipeline = MarketDataPipeline(provider, None, None, None, None)
    assert pipeline.live_feed is None


def test_ws_live_feed_uses_api_token_without_separate_index_credential(monkeypatch):
    """A real provider enters WS mode using the API access token only."""
    from providers.indmoney_provider import INDMoneyProvider

    monkeypatch.setenv("INDSTOCKS_ENABLE_WS_LIVE_QUOTES", "1")
    monkeypatch.setenv("INDSTOCKS_API_TOKEN", "api-token")
    monkeypatch.delenv("INDSTOCKS_WS_NIFTY_TOKEN", raising=False)
    provider = INDMoneyProvider.__new__(INDMoneyProvider)
    provider.token = "token"
    pipeline = MarketDataPipeline(provider, None, None, None, None)
    assert pipeline.live_feed is not None


def test_ws_index_instrument_resolves_from_authoritative_index_master(monkeypatch):
    from providers.indmoney_provider import INDMoneyProvider

    monkeypatch.setenv("INDSTOCKS_ENABLE_WS_LIVE_QUOTES", "1")
    provider = INDMoneyProvider.__new__(INDMoneyProvider)
    provider.token = "token"
    instrument = SimpleNamespace(get_index_security_id=lambda symbol: 40000001)
    pipeline = MarketDataPipeline(provider, instrument, None, None, None)
    assert pipeline.live_feed.index_instrument(instrument.get_index_security_id("NIFTY")) == "NIDX:40000001"


def test_rest_mode_remains_default(monkeypatch):
    monkeypatch.delenv("INDSTOCKS_ENABLE_WS_LIVE_QUOTES", raising=False)
    provider = SimpleNamespace(token="token")
    pipeline = MarketDataPipeline(provider, None, None, None, None)
    assert pipeline.live_feed is None
