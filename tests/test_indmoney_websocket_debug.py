import json
import time

import pytest

from providers.indmoney_websocket import (
    IndmoneyPriceFeed,
    LiveQuoteReceiveTimeout,
    summarize_websocket_message,
)


def test_summarize_websocket_message_reports_safe_control_metadata():
    summary = summarize_websocket_message({
        "type": "heartbeat",
        "status": "ok",
        "data": {"serverTime": 123},
    })
    assert summary["message_type"] == "control_or_other"
    assert summary["type"] == "heartbeat"
    assert summary["status"] == "ok"
    assert summary["data_keys"] == ["serverTime"]
    assert "token" not in summary


def test_summarize_websocket_message_reports_price_metadata_without_payload():
    summary = summarize_websocket_message({
        "mode": "ltp",
        "instrument": "26000",
        "timestamp": 1750138351089,
        "data": {"ltp": 24334.55},
    })
    assert summary == {
        "message_type": "price",
        "keys": ["data", "instrument", "mode", "timestamp"],
        "mode": "ltp",
        "instrument": "26000",
        "data_keys": ["ltp"],
    }


def test_summarize_websocket_message_classifies_plain_text():
    assert summarize_websocket_message("ping") == {
        "message_type": "non_json",
        "value_type": "str",
        "raw_length": 4,
        "string_kind": "ping",
    }


def test_summarize_websocket_message_bounds_and_redacts_plain_text_preview():
    message = "Authorization: SECRET_TOKEN " + ("x" * 200)
    summary = summarize_websocket_message(message)
    assert summary["message_type"] == "non_json"
    assert summary["value_type"] == "str"
    assert summary["raw_length"] == len(message)
    assert summary["preview_truncated"] is True
    assert "SECRET_TOKEN" not in summary["preview"]
    assert "[REDACTED]" in summary["preview"]
    assert len(summary["preview"]) <= 160


def test_summarize_websocket_message_classifies_json_scalar_string():
    summary = summarize_websocket_message(json.dumps("subscription acknowledged"))
    assert summary["message_type"] == "non_json"
    assert summary["value_type"] == "str"
    assert summary["preview"] == "subscription acknowledged"
    assert summary["preview_truncated"] is False


def test_recv_debug_returns_safe_message_summary():
    feed = IndmoneyPriceFeed("token", timeout=0.05)

    class Socket:
        def recv(self):
            return json.dumps({
                "type": "heartbeat",
                "status": "ok",
                "data": {"serverTime": 123},
            })

        def close(self):
            self.closed = True

    socket = Socket()
    feed._socket = socket
    summary = feed.recv_debug(timeout=0.05)
    assert summary["message_type"] == "control_or_other"
    assert summary["type"] == "heartbeat"
    assert summary["data_keys"] == ["serverTime"]


def test_recv_debug_reports_plain_text_message():
    feed = IndmoneyPriceFeed("token", timeout=0.05)

    class Socket:
        def recv(self):
            return "subscription acknowledged"

        def close(self):
            self.closed = True

    feed._socket = Socket()
    summary = feed.recv_debug(timeout=0.05)
    assert summary["message_type"] == "non_json"
    assert summary["value_type"] == "str"
    assert summary["preview"] == "subscription acknowledged"
    assert summary["preview_truncated"] is False


def test_recv_debug_hard_deadline_prevents_blocking_recv():
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

    with pytest.raises(LiveQuoteReceiveTimeout, match="debug receive exceeded"):
        feed.recv_debug()

    assert time.monotonic() - started < 0.5
    assert feed._socket is None
    assert socket.closed is True
