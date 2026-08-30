import json
from datetime import datetime, timezone

import pytest

from providers.indmoney_websocket import (
    IndmoneyPriceFeed,
    LiveQuoteReceiveTimeout,
    parse_price_feed_message,
    parse_timestamp_ms,
    websocket_instrument,
)


def test_parse_timestamp_ms_normalizes_to_utc():
    timestamp, timestamp_ms = parse_timestamp_ms(1750138351089)
    assert timestamp_ms == 1750138351089
    assert timestamp.tzinfo == timezone.utc
    assert timestamp == datetime.fromtimestamp(1750138351089 / 1000, tz=timezone.utc)


def test_parse_ltp_tick_preserves_provider_timestamp_and_ltp():
    tick = parse_price_feed_message(json.dumps({
        "mode": "ltp",
        "instrument": "40000001",
        "timestamp": 1750138351089,
        "data": {"ltp": 24334.55},
    }))
    assert tick is not None
    assert tick.instrument == "40000001"
    assert tick.timestamp_ms == 1750138351089
    assert tick.ltp == 24334.55
    assert tick.timestamp.tzinfo == timezone.utc


def test_parse_quote_tick_preserves_full_payload():
    payload = {
        "mode": "quote",
        "instrument": "46999",
        "timestamp": 1750138351089,
        "data": {"ltp": 100.25, "oi": 1200, "volume": 5000},
    }
    tick = parse_price_feed_message(payload)
    assert tick is not None
    assert tick.mode == "quote"
    assert tick.data == payload["data"]


def test_non_price_message_is_ignored():
    assert parse_price_feed_message({"type": "heartbeat"}) is None


def test_invalid_timestamp_is_rejected():
    with pytest.raises(ValueError):
        parse_price_feed_message({
            "mode": "ltp",
            "instrument": "40000001",
            "timestamp": None,
            "data": {"ltp": 24334.55},
        })


def test_websocket_instrument_uses_documented_segment_token_format():
    assert websocket_instrument("NIDX", 40000001) == "NIDX:40000001"
    assert websocket_instrument("NFO", 46999) == "NFO:46999"


def test_websocket_instrument_rejects_unknown_segment():
    with pytest.raises(ValueError):
        websocket_instrument("NIFTY", 40000001)


def test_price_feed_requires_token():
    with pytest.raises(ValueError):
        IndmoneyPriceFeed("")


def test_recv_tick_hard_deadline_prevents_blocking_recv(monkeypatch):
    feed = IndmoneyPriceFeed("token", timeout=0.1)

    class Socket:
        def settimeout(self, value):
            self.timeout = value

        def recv(self):
            raise AssertionError("recv must not be entered after select timeout")

    feed._socket = type("WebSocket", (), {"sock": Socket()})()
    monkeypatch.setattr("providers.indmoney_websocket.select.select", lambda *args: ([], [], []))

    with pytest.raises(LiveQuoteReceiveTimeout, match="no WebSocket price message"):
        feed.recv_tick()
