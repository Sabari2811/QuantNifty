from types import SimpleNamespace

from engine.market_data_pipeline import MarketDataPipeline
from providers.indmoney_provider import INDMoneyProvider


class _Instrument:
    def get_nearest_weekly_expiry(self, symbol):
        assert symbol == "NIFTY"
        return "2026-09-15"

    def get_index_security_id(self, symbol):
        assert symbol == "NIFTY"
        return 40000001


class _Market:
    def get_spot_quote(self, symbol):
        assert symbol == "NIFTY"
        return None


class _Provider:
    def get_index_option_chain_ltp(self, symbol, expiry, strike_count=1):
        assert symbol == "NIFTY"
        assert expiry == "2026-09-15"
        assert strike_count == 1
        return {"live_price": 23345.25, "provider_timestamp": None}


def _pipeline(provider=None):
    return MarketDataPipeline(
        provider=provider or _Provider(),
        instrument=_Instrument(),
        market=_Market(),
        chain_manager=SimpleNamespace(),
        candle_manager=SimpleNamespace(),
    )


def test_live_spot_uses_provider_option_chain_underlying_ltp_when_index_quote_unavailable():
    ctx = SimpleNamespace(symbol="NIFTY")
    _pipeline()._fetch_spot(ctx)

    assert ctx.spot == 23345.25
    assert ctx.data_provenance.spot.source == "INDMoney option-chain underlying LTP"
    assert ctx.data_provenance.spot.freshness_verified is False
    assert "index_quote_unavailable" in ctx.data_provenance.spot.reasons
    assert "provider_underlying_ltp_timestamp_unavailable" in ctx.data_provenance.spot.reasons


def test_provider_option_chain_ltp_reads_documented_underlying_value(monkeypatch):
    provider = INDMoneyProvider.__new__(INDMoneyProvider)
    provider.base_url = "https://api.indstocks.com"
    provider.headers = {"Authorization": "test-token"}

    class _Response:
        status_code = 200

        def raise_for_status(self):
            return None

        def json(self):
            return {"status": "success", "data": {"underlying_ltp": 23346.4}}

    def fake_get(url, headers, params, timeout):
        assert url.endswith("/market/option-chain")
        assert headers["Authorization"] == "test-token"
        assert params == {
            "exchange": "NSE",
            "segment": "INDEX",
            "underlying-scrip": 40000001,
            "expiry": "2026-09-15",
            "strike_count": 1,
        }
        assert timeout == 30
        return _Response()

    monkeypatch.setattr("providers.indmoney_provider.requests.get", fake_get)
    monkeypatch.setattr(
        "engine.instrument_manager.InstrumentManager",
        lambda: SimpleNamespace(get_index_security_id=lambda name: 40000001),
    )

    quote = provider.get_index_option_chain_ltp("NIFTY 50", "2026-09-15")

    assert quote == {"live_price": 23346.4, "provider_timestamp": None}
