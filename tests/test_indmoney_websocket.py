import json
import time
from datetime import datetime, timedelta, timezone

import pytest

from providers.indmoney_websocket import (
    IndmoneyPriceFeed,
    LiveQuoteConnectTimeout,
    LiveQuoteReceiveTimeout,
    assess_quote_freshness,
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
        "mode": "ltp", "instrument": "40000001", "timestamp": 1750138351089,
        "data": {"ltp": 24334.55},
    }))
    assert tick is not None
    assert tick.instrument == "40000001"
    assert tick.timestamp_ms == 1750138351089
    assert tick.ltp == 24334.55
    assert tick.timestamp.tzinfo == timezone.utc


def test_parse_double_encoded_ltp_tick_preserves_provider_fields():
    provider_payload = {
        "mode": "ltp", "instrument": "40000001", "timestamp": 1788325219350,
        "data": {"ltp": 23886.25},
    }
    message = json.dumps(json.dumps(provider_payload, separators=(",", ":")))
    tick = parse_price_feed_message(message)
    assert tick is not None
    assert tick.instrument == "40000001"
    assert tick.timestamp_ms == 1788325219350
    assert tick.mode == "ltp"
    assert tick.data == {"ltp": 23886.25}
    assert tick.ltp == 23886.25


def test_parse_quote_tick_preserves_full_payload():
    payload = {"mode": "quote", "instrument": "46999", "timestamp": 1750138351089,
               "data": {"ltp": 100.25, "oi": 1200, "volume": 5000}}
    tick = parse_price_feed_message(payload)
    assert tick is not None
    assert tick.mode == "quote"
    assert tick.data == payload["data"]


def test_non_price_message_is_ignored():
    assert parse_price_feed_message({"type": "heartbeat"}) is None


def test_invalid_timestamp_is_rejected():
    with pytest.raises(ValueError):
        parse_price_feed_message({"mode": "ltp", "instrument": "40000001", "timestamp": None,
                                  "data": {"ltp": 24334.55}})


def test_freshness_accepts_small_future_provider_timestamp_without_clamping():
    received_at = datetime(2026, 9, 2, 5, 2, 36, 614000, tzinfo=timezone.utc)
    tick = parse_price_feed_message({"mode": "ltp", "instrument": "40000001",
                                    "timestamp": int((received_at + timedelta(milliseconds=818)).timestamp() * 1000),
                                    "data": {"ltp": 23887.4}})
    result = assess_quote_freshness(tick, received_at=received_at)
    assert result.transport_age_ms == -818
    assert result.clock_skew_ms == 818
    assert result.status == "fresh_with_clock_skew"


def test_freshness_classifies_excessive_future_timestamp_as_clock_skew():
    received_at = datetime(2026, 9, 2, 5, 2, 36, tzinfo=timezone.utc)
    tick = parse_price_feed_message({"mode": "ltp", "instrument": "40000001",
                                    "timestamp": int((received_at + timedelta(seconds=3)).timestamp() * 1000),
                                    "data": {"ltp": 23887.4}})
    result = assess_quote_freshness(tick, received_at=received_at)
    assert result.transport_age_ms == -3000
    assert result.clock_skew_ms == 3000
    assert result.status == "clock_skew"


def test_freshness_classifies_old_quote_as_stale():
    received_at = datetime(2026, 9, 2, 5, 2, 36, tzinfo=timezone.utc)
    tick = parse_price_feed_message({"mode": "ltp", "instrument": "40000001",
                                    "timestamp": int((received_at - timedelta(seconds=3)).timestamp() * 1000),
                                    "data": {"ltp": 23887.4}})
    result = assess_quote_freshness(tick, received_at=received_at)
    assert result.transport_age_ms == 3000
    assert result.clock_skew_ms == 0
    assert result.status == "stale"


def test_freshness_requires_timezone_aware_receive_time():
    tick = parse_price_feed_message({"mode": "ltp", "instrument": "40000001", "timestamp": 1750138351089,
                                    "data": {"ltp": 24334.55}})
    with pytest.raises(ValueError, match="timezone-aware"):
        assess_quote_freshness(tick, received_at=datetime.now())


def test_websocket_instrument_uses_documented_segment_token_format():
    assert websocket_instrument("NIDX", 40000001) == "NIDX:40000001"
    assert websocket_instrument("NFO", 46999) == "NFO:46999"


def test_websocket_instrument_rejects_unknown_segment():
    with pytest.raises(ValueError):
        websocket_instrument("NIFTY", 40000001)


def test_price_feed_requires_token():
    with pytest.raises(ValueError):
        IndmoneyPriceFeed("")


def test_recv_tick_hard_deadline_prevents_blocking_recv():
    feed = IndmoneyPriceFeed("token", timeout=0.05)
    class Socket:
        def recv(self):
            time.sleep(1.0)
            return "never-reached"
        def close(self):
            self.closed = True
    socket = Socket()
    feed._socket = socket
    started = time.monotonic()
    with pytest.raises(LiveQuoteReceiveTimeout, match="price receive exceeded"):
        feed.recv_tick()
    assert time.monotonic() - started < 0.5
    assert feed._socket is None
    assert socket.closed is True


def test_connect_has_hard_wall_clock_deadline(monkeypatch):
    def blocking_connect(*args, **kwargs):
        time.sleep(1.0)
        raise OSError("simulated network hang")
    monkeypatch.setattr("providers.indmoney_websocket.websocket.create_connection", blocking_connect)
    feed = IndmoneyPriceFeed("token", timeout=0.05)
    started = time.monotonic()
    with pytest.raises(LiveQuoteConnectTimeout, match="connection exceeded"):
        feed.connect()
    assert time.monotonic() - started < 0.5
