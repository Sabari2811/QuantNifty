import os


def test_instrument_manager_accepts_render_apitoken_alias(monkeypatch):
    monkeypatch.delenv("INDSTOCKS_API_TOKEN", raising=False)
    monkeypatch.setenv("APITOKEN", "test-token")

    from engine.instrument_manager import InstrumentManager

    manager = InstrumentManager()

    assert manager.token == "test-token"
    assert manager.headers["Authorization"] == "test-token"


def test_instrument_manager_prefers_canonical_token(monkeypatch):
    monkeypatch.setenv("INDSTOCKS_API_TOKEN", "canonical-token")
    monkeypatch.setenv("APITOKEN", "alias-token")

    from engine.instrument_manager import InstrumentManager

    manager = InstrumentManager()

    assert manager.token == "canonical-token"
