from datetime import datetime, timezone

import pandas as pd

from engine.market_data_pipeline import MarketDataPipeline
from engine.option_chain_manager import OptionChainManager
from providers.indmoney_websocket import LiveQuoteFreshness


ACQUIRED = datetime(2026, 8, 30, 7, 0, 0, tzinfo=timezone.utc)


def test_spot_quote_timestamp_is_verified_when_provider_supplies_it():
    quote = {"live_price": 24175.65, "timestamp": "2026-08-30T06:59:58Z"}
    timestamp, verified, seconds, reasons = MarketDataPipeline._quote_freshness(quote, ACQUIRED)
    assert timestamp == datetime(2026, 8, 30, 6, 59, 58, tzinfo=timezone.utc)
    assert verified is True
    assert seconds == 2.0
    assert reasons == ("provider_quote_timestamp",)


def test_spot_quote_timestamp_is_not_invented():
    result = MarketDataPipeline._quote_freshness({"live_price": 24175.65}, ACQUIRED)
    assert result == (None, False, None, ("provider_quote_timestamp_unavailable",))


def test_future_provider_timestamp_is_not_verified():
    result = MarketDataPipeline._quote_freshness(
        {"live_price": 24175.65, "timestamp": "2026-08-30T07:00:01Z"}, ACQUIRED
    )
    assert result[0] == datetime(2026, 8, 30, 7, 0, 1, tzinfo=timezone.utc)
    assert result[1:] == (False, None, ("provider_quote_timestamp_in_future",))


def test_websocket_bounded_clock_skew_is_verified_and_explicit():
    provider_timestamp = datetime(2026, 8, 30, 7, 0, 0, 600000, tzinfo=timezone.utc)
    batch = type("Batch", (), {"freshness": {"NIDX:40000001": LiveQuoteFreshness(provider_timestamp, ACQUIRED, -600, 600, "fresh_with_clock_skew")}})()
    assert MarketDataPipeline._websocket_freshness(batch, "NIDX:40000001") == (
        provider_timestamp, True, -0.6,
        ("provider_quote_timestamp", "provider_quote_timestamp_clock_skew"),
    )


def test_websocket_excessive_clock_skew_is_not_verified():
    provider_timestamp = datetime(2026, 8, 30, 7, 0, 3, tzinfo=timezone.utc)
    batch = type("Batch", (), {"freshness": {"NIDX:40000001": LiveQuoteFreshness(provider_timestamp, ACQUIRED, -3000, 3000, "clock_skew")}})()
    assert MarketDataPipeline._websocket_freshness(batch, "NIDX:40000001") == (
        provider_timestamp, False, None,
        ("provider_quote_timestamp", "provider_quote_timestamp_clock_skew_excessive"),
    )


class _Provider:
    def get_quotes(self, security_ids):
        return {f"NFO_{sid}": {"live_price": 100.0, "open_interest": 1000, "volume": 100, "timestamp": "2026-08-30T06:59:58Z"} for sid in security_ids}


class _Selector:
    def get_option_security_ids(self, **kwargs):
        return [{"strike": 25000, "CE_ID": 111, "PE_ID": 222}]


class _Instrument:
    def get_nearest_weekly_expiry(self, symbol):
        return "09/01/2026 14:00"


class _Market:
    pass


def test_option_chain_uses_provider_timestamp_for_freshness(monkeypatch):
    manager = OptionChainManager(_Provider(), _Selector(), _Instrument(), _Market())
    monkeypatch.setattr("engine.option_chain_manager.datetime", type("FixedDatetime", (), {"now": staticmethod(lambda tz=None: ACQUIRED)}))
    chain = manager.get_live_option_chain("NIFTY", 25000, levels=0)
    provenance = chain.attrs["data_provenance"]
    assert isinstance(chain, pd.DataFrame)
    assert provenance.provider_timestamp == datetime(2026, 8, 30, 6, 59, 58, tzinfo=timezone.utc)
    assert provenance.freshness_verified is True
    assert provenance.freshness_seconds == 2.0
    assert provenance.reasons == ("provider_quote_timestamp",)
