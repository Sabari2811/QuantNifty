from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable

from providers.indmoney_websocket import (
    IndmoneyPriceFeed,
    LiveQuoteFreshness,
    LiveQuoteReceiveTimeout,
    LiveQuoteTick,
    assess_quote_freshness,
    websocket_instrument,
)


@dataclass(frozen=True, slots=True)
class LiveQuoteBatch:
    """Timestamp-bearing ticks collected for one canonical market snapshot."""

    ticks: dict[str, LiveQuoteTick]
    received_at: dict[str, datetime]
    freshness: dict[str, LiveQuoteFreshness]
    acquired_at: datetime
    connected_at: datetime
    completed_at: datetime

    @property
    def latest_provider_timestamp(self) -> datetime | None:
        timestamps = [tick.timestamp for tick in self.ticks.values()]
        return max(timestamps) if timestamps else None

    @property
    def freshness_verified(self) -> bool:
        return bool(self.ticks) and all(
            assessment.status in {"fresh", "fresh_with_clock_skew"}
            for assessment in self.freshness.values()
        ) and len(self.freshness) == len(self.ticks)

    @property
    def freshness_reasons(self) -> tuple[str, ...]:
        reasons: list[str] = []
        for assessment in self.freshness.values():
            if assessment.status == "fresh_with_clock_skew":
                reasons.append("provider_quote_timestamp_clock_skew")
            elif assessment.status == "clock_skew":
                reasons.append("provider_quote_timestamp_clock_skew_excessive")
            elif assessment.status == "stale":
                reasons.append("provider_quote_timestamp_stale")
            else:
                reasons.append("provider_quote_timestamp")
        return tuple(dict.fromkeys(reasons))


class LiveQuoteCoordinator:
    """Persistent INDstocks quote stream for the NIFTY hot path.

    A connection is opened lazily and reused across cycles. REST remains the
    fallback/recovery path; the hot path must not reconnect the WebSocket on
    every cycle.
    """

    def __init__(self, access_token: str, *, timeout: float = 10.0):
        self.access_token = access_token
        self.timeout = timeout
        self._feed: IndmoneyPriceFeed | None = None
        self._connected_at: datetime | None = None

    def _ensure_feed(self) -> IndmoneyPriceFeed:
        if self._feed is not None:
            return self._feed
        feed = IndmoneyPriceFeed(self.access_token, timeout=self.timeout)
        feed.connect()
        self._feed = feed
        self._connected_at = datetime.now(timezone.utc)
        return feed

    def _reset_feed(self) -> None:
        feed, self._feed = self._feed, None
        self._connected_at = None
        if feed is not None:
            feed.close()

    @staticmethod
    def _matches_requested(tick: LiveQuoteTick, requested: set[str]) -> str | None:
        if tick.instrument in requested:
            return tick.instrument
        matches = [
            item for item in requested
            if item.rsplit(":", 1)[-1] == tick.instrument
        ]
        return matches[0] if len(matches) == 1 else None

    def collect(self, instruments: Iterable[str], *, mode: str = "quote") -> LiveQuoteBatch:
        requested = list(dict.fromkeys(str(value) for value in instruments))
        if not requested:
            raise ValueError("at least one instrument is required")
        requested_set = set(requested)
        started_at = datetime.now(timezone.utc)
        last_error: Exception | None = None

        for attempt in range(2):
            try:
                feed = self._ensure_feed()
                connected_at = self._connected_at or started_at
                feed.subscribe(requested, mode=mode)
                ticks: dict[str, LiveQuoteTick] = {}
                received_at: dict[str, datetime] = {}
                freshness: dict[str, LiveQuoteFreshness] = {}
                deadline = started_at.timestamp() + self.timeout
                while len(ticks) < len(requested) and datetime.now(timezone.utc).timestamp() < deadline:
                    remaining = max(0.05, deadline - datetime.now(timezone.utc).timestamp())
                    tick = feed.recv_tick(timeout=remaining)
                    observed_at = datetime.now(timezone.utc)
                    if tick is None:
                        continue
                    requested_instrument = self._matches_requested(tick, requested_set)
                    if requested_instrument is None:
                        continue
                    current = ticks.get(requested_instrument)
                    if current is None or tick.timestamp_ms >= current.timestamp_ms:
                        ticks[requested_instrument] = tick
                        received_at[requested_instrument] = observed_at
                        freshness[requested_instrument] = assess_quote_freshness(tick, received_at=observed_at)
                completed_at = datetime.now(timezone.utc)
                return LiveQuoteBatch(
                    ticks=ticks,
                    received_at=received_at,
                    freshness=freshness,
                    acquired_at=completed_at,
                    connected_at=connected_at,
                    completed_at=completed_at,
                )
            except (LiveQuoteReceiveTimeout, OSError, RuntimeError) as exc:
                last_error = exc
                self._reset_feed()
                if attempt == 0:
                    continue
                raise
        raise RuntimeError("Unable to collect live quote batch") from last_error

    def close(self) -> None:
        self._reset_feed()

    def __enter__(self) -> "LiveQuoteCoordinator":
        self._ensure_feed()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    @staticmethod
    def option_instrument(security_id: int | str) -> str:
        return websocket_instrument("NFO", security_id)

    @staticmethod
    def index_instrument(security_id: int | str) -> str:
        return websocket_instrument("NIDX", security_id)
