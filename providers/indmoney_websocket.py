from __future__ import annotations

import json
import select
import socket
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable

import websocket


PRICE_FEED_URL = "wss://ws-prices.indstocks.com/api/v1/ws/prices"


class LiveQuoteReceiveTimeout(TimeoutError):
    """Raised when no complete WebSocket price message arrives before a deadline."""


class LiveQuoteConnectTimeout(TimeoutError):
    """Raised when the WebSocket connection cannot be established before a deadline."""


@dataclass(frozen=True, slots=True)
class LiveQuoteTick:
    """Timestamp-bearing quote received from the INDstocks price feed."""

    instrument: str
    timestamp: datetime
    timestamp_ms: int
    mode: str
    data: dict[str, Any]

    @property
    def ltp(self) -> float | None:
        value = self.data.get("ltp")
        try:
            return None if value is None else float(value)
        except (TypeError, ValueError):
            return None


def parse_timestamp_ms(value: Any) -> tuple[datetime, int]:
    """Normalize a WebSocket epoch-millisecond timestamp to UTC."""
    try:
        timestamp_ms = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("invalid WebSocket timestamp") from exc
    if timestamp_ms <= 0:
        raise ValueError("WebSocket timestamp must be positive")
    timestamp = datetime.fromtimestamp(timestamp_ms / 1000.0, tz=timezone.utc)
    return timestamp, timestamp_ms


def parse_price_feed_message(message: str | bytes | dict[str, Any]) -> LiveQuoteTick | None:
    """Parse one INDstocks price-feed message; ignore heartbeat/non-price payloads."""
    if isinstance(message, bytes):
        message = message.decode("utf-8")
    payload = json.loads(message) if isinstance(message, str) else message
    if not isinstance(payload, dict):
        return None
    mode = str(payload.get("mode", ""))
    if mode not in {"ltp", "quote"}:
        return None
    instrument = payload.get("instrument")
    data = payload.get("data")
    if instrument is None or not isinstance(data, dict):
        return None
    timestamp, timestamp_ms = parse_timestamp_ms(payload.get("timestamp"))
    return LiveQuoteTick(
        instrument=str(instrument),
        timestamp=timestamp,
        timestamp_ms=timestamp_ms,
        mode=mode,
        data=dict(data),
    )


def websocket_instrument(segment: str, security_id: int | str) -> str:
    """Build the SEGMENT:TOKEN format required by the INDstocks WebSocket."""
    normalized = str(segment).upper().strip()
    if normalized not in {"NSE", "BSE", "NFO", "BFO", "NIDX", "BIDX"}:
        raise ValueError(f"unsupported WebSocket segment: {segment}")
    return f"{normalized}:{security_id}"


class IndmoneyPriceFeed:
    """Synchronous INDstocks price-feed client with bounded I/O."""

    def __init__(self, access_token: str, *, url: str = PRICE_FEED_URL, timeout: float = 10.0) -> None:
        if not access_token:
            raise ValueError("access_token is required")
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        self.access_token = access_token
        self.url = url
        self.timeout = float(timeout)
        self._socket: websocket.WebSocket | None = None

    def connect(self) -> None:
        """Establish the socket without allowing a blocking transport to freeze the caller."""
        result: dict[str, Any] = {}
        finished = threading.Event()

        def worker() -> None:
            try:
                result["socket"] = websocket.create_connection(
                    self.url,
                    timeout=self.timeout,
                    header=[f"Authorization: {self.access_token}"],
                )
            except BaseException as exc:
                result["error"] = exc
            finally:
                finished.set()

        thread = threading.Thread(target=worker, name="indstocks-ws-connect", daemon=True)
        thread.start()
        if not finished.wait(self.timeout):
            raise LiveQuoteConnectTimeout(f"WebSocket connection exceeded {self.timeout:.1f}s")
        error = result.get("error")
        if error is not None:
            raise error
        self._socket = result.get("socket")
        if self._socket is None:
            raise LiveQuoteConnectTimeout("WebSocket connection returned no socket")

    def subscribe(self, instruments: Iterable[str], mode: str = "quote") -> None:
        if mode not in {"ltp", "quote"}:
            raise ValueError("mode must be 'ltp' or 'quote'")
        if self._socket is None:
            raise RuntimeError("price feed is not connected")
        payload = {"action": "subscribe", "mode": mode, "instruments": list(instruments)}
        if not payload["instruments"]:
            raise ValueError("at least one instrument is required")
        self._socket.send(json.dumps(payload))

    def recv_tick(self, timeout: float | None = None) -> LiveQuoteTick | None:
        if self._socket is None:
            raise RuntimeError("price feed is not connected")
        effective_timeout = self.timeout if timeout is None else float(timeout)
        if effective_timeout <= 0:
            raise ValueError("timeout must be positive")

        result: dict[str, Any] = {}
        finished = threading.Event()
        socket_obj = self._socket

        def worker() -> None:
            try:
                result["message"] = socket_obj.recv()
            except BaseException as exc:
                result["error"] = exc
            finally:
                finished.set()

        thread = threading.Thread(target=worker, name="indstocks-ws-recv", daemon=True)
        thread.start()
        if not finished.wait(effective_timeout):
            try:
                socket_obj.close()
            finally:
                self._socket = None
            raise LiveQuoteReceiveTimeout(
                f"WebSocket price receive exceeded {effective_timeout:.1f}s"
            )

        error = result.get("error")
        if error is not None:
            if isinstance(error, (websocket.WebSocketTimeoutException, TimeoutError, socket.timeout)):
                raise LiveQuoteReceiveTimeout(
                    f"WebSocket price receive exceeded {effective_timeout:.1f}s"
                ) from error
            raise error
        return parse_price_feed_message(result.get("message"))

    def iter_ticks(self, *, max_ticks: int | None = None, timeout: float | None = None):
        if self._socket is None:
            raise RuntimeError("price feed is not connected")
        effective_timeout = self.timeout if timeout is None else float(timeout)
        if effective_timeout <= 0:
            raise ValueError("timeout must be positive")
        received = 0
        while max_ticks is None or received < max_ticks:
            tick = self.recv_tick(timeout=effective_timeout)
            if tick is None:
                continue
            received += 1
            yield tick

    def close(self) -> None:
        if self._socket is not None:
            try:
                self._socket.close()
            finally:
                self._socket = None

    def __enter__(self) -> "IndmoneyPriceFeed":
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
