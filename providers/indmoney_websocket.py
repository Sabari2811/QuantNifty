from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable

import websocket


PRICE_FEED_URL = "wss://ws-prices.indstocks.com/api/v1/ws/prices"


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
    """Small synchronous price-feed client with explicit timestamp propagation.

    The client is intentionally transport-focused. It does not mutate the
    canonical runtime state; callers decide which tick is authoritative.
    """

    def __init__(
        self,
        access_token: str,
        *,
        url: str = PRICE_FEED_URL,
        timeout: float = 10.0,
    ) -> None:
        if not access_token:
            raise ValueError("access_token is required")
        self.access_token = access_token
        self.url = url
        self.timeout = timeout
        self._socket: websocket.WebSocket | None = None

    def connect(self) -> None:
        self._socket = websocket.create_connection(
            self.url,
            timeout=self.timeout,
            header=[f"Authorization: {self.access_token}"],
        )

    def subscribe(self, instruments: Iterable[str], mode: str = "quote") -> None:
        if mode not in {"ltp", "quote"}:
            raise ValueError("mode must be 'ltp' or 'quote'")
        if self._socket is None:
            raise RuntimeError("price feed is not connected")
        payload = {
            "action": "subscribe",
            "mode": mode,
            "instruments": list(instruments),
        }
        if not payload["instruments"]:
            raise ValueError("at least one instrument is required")
        self._socket.send(json.dumps(payload))

    def recv_tick(self) -> LiveQuoteTick | None:
        if self._socket is None:
            raise RuntimeError("price feed is not connected")
        return parse_price_feed_message(self._socket.recv())

    def iter_ticks(self, *, max_ticks: int | None = None, timeout: float | None = None):
        if self._socket is None:
            raise RuntimeError("price feed is not connected")
        if timeout is not None:
            self._socket.settimeout(timeout)
        received = 0
        while max_ticks is None or received < max_ticks:
            tick = self.recv_tick()
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
