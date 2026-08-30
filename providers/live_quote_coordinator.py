from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable

from providers.indmoney_websocket import IndmoneyPriceFeed, LiveQuoteTick, websocket_instrument


@dataclass(frozen=True, slots=True)
class LiveQuoteBatch:
    """Timestamp-bearing ticks collected for one canonical market snapshot."""

    ticks: dict[str, LiveQuoteTick]
    acquired_at: datetime

    @property
    def latest_provider_timestamp(self) -> datetime | None:
        timestamps = [tick.timestamp for tick in self.ticks.values()]
        return max(timestamps) if timestamps else None


class LiveQuoteCoordinator:
    """Collect one timestamp-bearing quote tick per requested instrument."""

    def __init__(self, access_token: str, *, timeout: float = 10.0):
        self.access_token = access_token
        self.timeout = timeout

    def collect(self, instruments: Iterable[str], *, mode: str = "quote") -> LiveQuoteBatch:
        requested = list(dict.fromkeys(str(value) for value in instruments))
        if not requested:
            raise ValueError("at least one instrument is required")
        started_at = datetime.now(timezone.utc)
        ticks: dict[str, LiveQuoteTick] = {}
        with IndmoneyPriceFeed(self.access_token, timeout=self.timeout) as feed:
            feed.subscribe(requested, mode=mode)
            deadline = started_at.timestamp() + self.timeout
            while len(ticks) < len(requested) and datetime.now(timezone.utc).timestamp() < deadline:
                tick = feed.recv_tick()
                if tick is None or tick.instrument not in requested:
                    continue
                current = ticks.get(tick.instrument)
                if current is None or tick.timestamp_ms >= current.timestamp_ms:
                    ticks[tick.instrument] = tick
        return LiveQuoteBatch(ticks=ticks, acquired_at=datetime.now(timezone.utc))

    @staticmethod
    def option_instrument(security_id: int | str) -> str:
        return websocket_instrument("NFO", security_id)

    @staticmethod
    def index_instrument(security_id: int | str) -> str:
        return websocket_instrument("NIDX", security_id)
