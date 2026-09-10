"""Deterministic adaptive-learning layer for live validation.

The Brain is downstream of the authoritative decision/analytics pipeline. It
never changes a live decision. It captures market fingerprints, uses only
resolved outcomes for learning, and restores learned history after restart.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any

from analytics.intelligence.feature_extractor import FeatureExtractor
from analytics.intelligence.memory_engine import MarketMemory
from analytics.intelligence.models import TradeIntelligenceRecord
from analytics.intelligence.similarity_engine import SimilarityEngine
from monitoring.durable_store import SqlAppendStore


@dataclass(frozen=True, slots=True)
class BrainObservation:
    status: str
    cycle_no: int
    signal: str
    similarity: float
    historical_win_rate: float
    outcome: str
    persisted: bool


class BrainStore:
    """Append-only Brain persistence with SQL durability when configured."""

    def __init__(
        self,
        path: str | os.PathLike[str] | None = None,
        database_url: str | None = None,
    ):
        self._sql_store = None
        configured_url = (
            database_url
            or os.getenv("BRAIN_DATABASE_URL")
            or os.getenv("LIVE_EVIDENCE_DATABASE_URL")
            or os.getenv("PAPER_TRADE_DATABASE_URL")
        )
        if configured_url:
            self._sql_store = SqlAppendStore(configured_url, "brain_observations")
            self.path = None
        else:
            self.path = Path(path or os.getenv("BRAIN_STORE_PATH", "runtime_data/brain.jsonl"))
            self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, record: Any) -> None:
        payload = asdict(record) if hasattr(record, "__dataclass_fields__") else dict(record)
        if self._sql_store is not None:
            self._sql_store.append(payload)
            return
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(payload, default=str, sort_keys=True) + "\n")
            fh.flush()
            os.fsync(fh.fileno())

    def records(self) -> list[dict[str, Any]]:
        if self._sql_store is not None:
            return self._sql_store.records()
        if not self.path.exists():
            return []
        records = []
        with self.path.open("r", encoding="utf-8") as fh:
            for line in fh:
                if not line.strip():
                    continue
                try:
                    payload = json.loads(line)
                    if isinstance(payload, dict):
                        records.append(payload)
                except json.JSONDecodeError:
                    # A torn final line must not destroy prior learned history.
                    continue
        return records

    def count(self) -> int:
        if self._sql_store is not None:
            return self._sql_store.count()
        return len(self.records())

    def close(self) -> None:
        if self._sql_store is not None:
            self._sql_store.close()


class AdaptiveBrain:
    """Capture fingerprints and learn only from resolved paper/live outcomes."""

    def __init__(self, store: BrainStore | None = None):
        self.extractor = FeatureExtractor()
        self.similarity = SimilarityEngine()
        self.memory = MarketMemory()
        self.store = store or BrainStore()
        self._restore_history()

    def _restore_history(self) -> None:
        for payload in self.store.records():
            raw = payload.get("record")
            if not isinstance(raw, dict):
                continue
            try:
                fields = {k: v for k, v in raw.items() if k in TradeIntelligenceRecord.__dataclass_fields__}
                if isinstance(fields.get("reasons"), list):
                    fields["reasons"] = list(fields["reasons"])
                self.memory.add(TradeIntelligenceRecord(**fields))
            except (TypeError, ValueError):
                continue

    @staticmethod
    def _resolved_trade(ctx: Any, broker: Any = None) -> Any:
        broker = broker or getattr(ctx, "paper_broker", None)
        trade = getattr(broker, "last_trade", None) if broker else None
        if trade is None or not getattr(trade, "closed", False):
            return None
        if getattr(trade, "pnl", None) is None:
            return None
        try:
            float(trade.pnl)
        except (TypeError, ValueError):
            return None
        return trade

    @classmethod
    def _resolved_outcome(cls, ctx: Any, broker: Any = None) -> str:
        trade = cls._resolved_trade(ctx, broker)
        if trade is None:
            return ""
        return "WIN" if float(trade.pnl) > 0 else "LOSS"

    def _already_learned(self, trade_id: str) -> bool:
        if not trade_id:
            return False
        return any(
            str(payload.get("trade_id") or "") == trade_id
            and payload.get("outcome") in {"WIN", "LOSS"}
            for payload in self.store.records()
        )

    def observe(self, ctx: Any, broker: Any = None) -> BrainObservation:
        record = self.extractor.extract(ctx)
        trade = self._resolved_trade(ctx, broker)
        outcome = self._resolved_outcome(ctx, broker)
        trade_id = str(
            getattr(getattr(trade, "order", None), "order_id", "")
            or getattr(trade, "order_id", "")
            or ""
        )
        duplicate_outcome = bool(outcome and self._already_learned(trade_id))
        if outcome and not duplicate_outcome:
            record.outcome = outcome

        historical = [r for r in self.memory.records if r.outcome in {"WIN", "LOSS"}]
        matches = self.similarity.search(record, historical, top_n=20)
        similarity = float(matches[0][0]) if matches else 0.0
        signal_records = [r for r in historical if r.signal == record.signal]
        wins = sum(1 for r in signal_records if r.outcome == "WIN")
        win_rate = (wins / len(signal_records) * 100.0) if signal_records else 0.0
        record.similarity_score = similarity
        record.historical_win_rate = round(win_rate, 2)

        self.store.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cycle_no": int(getattr(ctx, "cycle_no", 0) or 0),
            "signal": record.signal,
            "outcome": outcome if not duplicate_outcome else "",
            "trade_id": trade_id,
            "duplicate_outcome": duplicate_outcome,
            "similarity_score": record.similarity_score,
            "historical_win_rate": record.historical_win_rate,
            "record": asdict(record),
        })
        # Only the first resolved observation for a real trade enters learned
        # memory. Repeated market cycles may still be persisted as telemetry.
        if not duplicate_outcome:
            self.memory.add(record)

        status = "LEARNED" if outcome and not duplicate_outcome else ("ALREADY_LEARNED" if duplicate_outcome else "WAITING_OUTCOME")
        return BrainObservation(
            status=status,
            cycle_no=int(getattr(ctx, "cycle_no", 0) or 0),
            signal=str(record.signal or ""),
            similarity=record.similarity_score,
            historical_win_rate=record.historical_win_rate,
            outcome=outcome if not duplicate_outcome else "",
            persisted=True,
        )
