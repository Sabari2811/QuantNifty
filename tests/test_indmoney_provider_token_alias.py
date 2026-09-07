import pytest

from providers.indmoney_provider import INDMoneyProvider


def test_indmoney_provider_accepts_live_render_apitoken(monkeypatch):
    monkeypatch.delenv("INDSTOCKS_API_TOKEN", raising=False)
    monkeypatch.setenv("APITOKEN", "render-live-token")

    provider = INDMoneyProvider()

    assert provider.token == "render-live-token"
    assert provider.headers["Authorization"] == "render-live-token"


def test_indmoney_provider_prefers_explicit_indstocks_token(monkeypatch):
    monkeypatch.setenv("APITOKEN", "render-live-token")
    monkeypatch.setenv("INDSTOCKS_API_TOKEN", "explicit-ci-token")

    provider = INDMoneyProvider()

    assert provider.token == "explicit-ci-token"
    assert provider.headers["Authorization"] == "explicit-ci-token"


def test_indmoney_provider_rejects_missing_tokens(monkeypatch):
    monkeypatch.delenv("INDSTOCKS_API_TOKEN", raising=False)
    monkeypatch.delenv("APITOKEN", raising=False)

    with pytest.raises(Exception, match="INDSTOCKS_API_TOKEN or APITOKEN"):
        INDMoneyProvider()
