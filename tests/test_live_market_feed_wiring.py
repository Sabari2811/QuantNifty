from types import SimpleNamespace

import pytest

from engine.market_data_pipeline import MarketDataPipeline


def test_ws_live_feed_requires_explicit_index_token(monkeypatch):
    """Production WS validation applies only to the real INDMoney provider."""
    monkeypatch.setenv("INDSTOCKS_ENABLE_WS_LIVE_QUOTES", "1")
    monkeypatch.setenv("INDSTOCKS_API_TOKEN", "api-token")
    monkeypatch.delenv("INDSTOCKS_WS_NIFTY_TOKEN", raising=False)
    provider = SimpleNamespace(token="token")
    pipeline = MarketDataPipeline(provider, None, None, None, None)
    assert pipeline.live_feed is None


def test_ws_live_feed_requires_index_token_for_indmoney_provider(monkeypatch):
    """A real INDMoney provider cannot enter WS mode without an explicit index token."""
    from providers.indmoney_provider import INDMoneyProvider

    monkeypatch.setenv("INDSTOCKS_ENABLE_WS_LIVE_QUOTES", "1")
    monkeypatch.setenv("INDSTOCKS_API_TOKEN", "api-token")
    monkeypatch.delenv("INDSTOCKS_WS_NIFTY_TOKEN", raising=False)
    provider = INDMoneyProvider.__new__(INDMoneyProvider)
    provider.token = "token"
    with pytest.raises(RuntimeError, match="INDSTOCKS_WS_NIFTY_TOKEN"):
        MarketDataPipeline(provider, None, None, None, None)


def test_rest_mode_remains_default(monkeypatch):
    monkeypatch.delenv("INDSTOCKS_ENABLE_WS_LIVE_QUOTES", raising=False)
    provider = SimpleNamespace(token="token")
    pipeline = MarketDataPipeline(provider, None, None, None, None)
    assert pipeline.live_feed is None
