from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class SessionMetadata:
    """
    Metadata describing one recorded trading session.

    One Session
        ↓
    Many Snapshots
    """

    session_id: str

    symbol: str = "NIFTY"

    started_at: datetime | None = None

    ended_at: datetime | None = None

    status: str = "OPEN"

    snapshot_count: int = 0

    last_snapshot: str | None = None

    # =====================================================
    # Helpers
    # =====================================================

    def increment(self):

        self.snapshot_count += 1

    def close(self):

        self.status = "CLOSED"

        self.ended_at = datetime.now()