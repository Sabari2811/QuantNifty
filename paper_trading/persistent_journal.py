"""Durable paper-trade journal used by the validation/runtime broker."""
from __future__ import annotations

import os
from datetime import datetime
from dataclasses import asdict

from paper_trading.journal import TradeJournal
from paper_trading.models import TradeRecord
from monitoring.durable_store import SqlAppendStore


class PersistentTradeJournal(TradeJournal):
    """TradeJournal with SQL durability when a production database is configured."""

    def __init__(self, database_url: str | None = None):
        super().__init__()
        self._store = None
        url = (
            database_url
            or os.getenv("PAPER_TRADE_DATABASE_URL")
            or os.getenv("BRAIN_DATABASE_URL")
            or os.getenv("LIVE_EVIDENCE_DATABASE_URL")
        )
        if url:
            self._store = SqlAppendStore(url, "paper_trades")
            self._restore()

    @staticmethod
    def _datetime(value):
        if isinstance(value, datetime):
            return value
        if value is None:
            return datetime.now()
        try:
            return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except (TypeError, ValueError):
            return datetime.now()

    def _restore(self):
        for payload in self._store.records():
            try:
                fields = dict(payload)
                fields["entry_time"] = self._datetime(fields.get("entry_time"))
                fields["exit_time"] = self._datetime(fields.get("exit_time"))
                self.records.append(TradeRecord(**fields))
            except (TypeError, ValueError):
                continue

    def record(self, position, exit_reason):
        record = super().record(position, exit_reason)
        if self._store is not None:
            self._store.append(asdict(record))
        return record

    def close(self):
        if self._store is not None:
            self._store.close()
