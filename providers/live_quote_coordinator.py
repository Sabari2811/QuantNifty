from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable

from providers.indmoney_websocket import IndmoneyPriceFeed, LiveQuoteTick, websocket_instrument


@dataclass(frozen=True, slots=True)
class LiveQuoteBatch:
    """Timestamp-bearing ticks collected for one canonical market snapshot."""

    ticks: dict[str, LiveQuoteTick]
    received_at: dict[str, datetime]
    acquired_at: datetime
    connected_at: datetime
    completed_at: datetime

    @property
    def latest_provider_timestamp(self) -> datetime | None:
        timestamps = [tick.timestamp for tick in self.ticks.values()]
        return max(timestamps) if timestamps else None


class LiveQuoteCoordinator:
    """Collect one timestamp-bearing quote tick per requested instrument."""

    def __init__(self, access_token: str, *, timeout: float = 10.0):
        self.access_token = access_token
        self.timeout = timeout

    @staticmethod
    def _matches_requested(tick: LiveQuoteTick, requested: set[str]) -> str | None:
        """Return the requested instrument represented by a provider tick.

        INDstocks subscription identifiers may be segment-qualified (for
        example ``NIDX:40000001``) while the returned price message observed
        in live validation contains only ``40000001``. Match only exact IDs
        or an unambiguous segment-suffix match; never synthesize identity.
        """
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
        ticks: dict[str, LiveQuoteTick] = {}
        received_at: dict[str, datetime] = {}
        with IndmoneyPriceFeed(self.access_token, timeout=self.timeout) as feed:
            connected_at = datetime.now(timezone.utc)
            feed.subscribe(requested, mode=mode)
            deadline = started_at.timestamp() + self.timeout
            while len(ticks) < len(requested) and datetime.now(timezone.utc).timestamp() < deadline:
                tick = feed.recv_tick()
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
            completed_at = datetime.now(timezone.utc)
        return LiveQuoteBatch(
            ticks=ticks,
            received_at=received_at,
            acquired_at=completed_at,
            connected_at=connected_at,
            completed_at=completed_at,
        )

    @staticmethod
    def option_instrument(security_id: int | str) -> str:
        return websocket_instrument("NFO", security_id)

    @staticmethod
    def index_instrument(security_id: int | str) -> str:
        return websocket_instrument("NIDX", security_id)
