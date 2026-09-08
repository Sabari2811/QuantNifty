"""Deterministic adaptive-learning layer for live validation.

The Brain is downstream of the authoritative decision/analytics pipeline. It
never changes a live decision. It captures the market fingerprint, uses only
resolved outcomes for learning, and keeps unresolved observations pending.
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
from analytics.intelligence.similarity_engine import SimilarityEngine


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
    """Append-only JSONL persistence for Brain observations."""

    def __init__(self, path: str | os.PathLike[str] | None = None):
        self.path = Path(path or os.getenv("BRAIN_STORE_PATH", "runtime_data/brain.jsonl"))
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, record: Any) -> None:
        payload = asdict(record) if hasattr(record, "__dataclass_fields__") else dict(record)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(payload, default=str, sort_keys=True) + "\n")
            fh.flush()
            os.fsync(fh.fileno())

    def count(self) -> int:
        if not self.path.exists():
            return 0
        with self.path.open("r", encoding="utf-8") as fh:
            return sum(1 for line in fh if line.strip())


class AdaptiveBrain:
    """Capture fingerprints and learn only from resolved paper/live outcomes."""

    def __init__(self, store: BrainStore | None = None):
        self.extractor = FeatureExtractor()
        self.similarity = SimilarityEngine()
        self.memory = MarketMemory()
        self.store = store or BrainStore()

    @staticmethod
    def _resolved_outcome(ctx: Any, broker: Any = None) -> str:
        broker = broker or getattr(ctx, "paper_broker", None)
        trade = getattr(broker, "last_trade", None) if broker else None
        if trade is None or not getattr(trade, "closed", False):
            return ""
        pnl = getattr(trade, "pnl", None)
        if pnl is None:
            return ""
        try:
            return "WIN" if float(pnl) > 0 else "LOSS"
        except (TypeError, ValueError):
            return ""

    def observe(self, ctx: Any, broker: Any = None) -> BrainObservation:
        record = self.extractor.extract(ctx)
        outcome = self._resolved_outcome(ctx, broker)
        if outcome:
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
            "outcome": record.outcome,
            "similarity_score": record.similarity_score,
            "historical_win_rate": record.historical_win_rate,
            "record": asdict(record),
        })
        self.memory.add(record)

        status = "LEARNED" if outcome else "WAITING_OUTCOME"
        return BrainObservation(
            status=status,
            cycle_no=int(getattr(ctx, "cycle_no", 0) or 0),
            signal=str(record.signal or ""),
            similarity=record.similarity_score,
            historical_win_rate=record.historical_win_rate,
            outcome=outcome,
            persisted=True,
        )
