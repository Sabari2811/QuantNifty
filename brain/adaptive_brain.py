"""Deterministic online-learning layer for the NIFTY decision engine.

The Brain is intentionally conservative. It never invents CALL vs PUT; the
canonical NIFTY analytics direction remains authoritative. The Brain learns
only from resolved trades and may veto a repeated pattern when enough similar
historical evidence shows that the pattern is not profitable.
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
class BrainDecision:
    status: str
    signal: str
    similarity: float
    historical_win_rate: float
    average_pnl: float
    sample_count: int
    matching_wins: int
    matching_losses: int
    gate: str
    reason: str


@dataclass(frozen=True, slots=True)
class BrainObservation:
    status: str
    cycle_no: int
    signal: str
    similarity: float
    historical_win_rate: float
    outcome: str
    persisted: bool
    trade_id: str = ""
    learning_sample_count: int = 0


class BrainStore:
    """Append-only Brain persistence with SQL durability when configured."""

    def __init__(self, path: str | os.PathLike[str] | None = None, database_url: str | None = None):
        self._sql_store = None
        configured_url = database_url or os.getenv("BRAIN_DATABASE_URL") or os.getenv("LIVE_EVIDENCE_DATABASE_URL") or os.getenv("PAPER_TRADE_DATABASE_URL")
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
        records: list[dict[str, Any]] = []
        with self.path.open("r", encoding="utf-8") as fh:
            for line in fh:
                if not line.strip():
                    continue
                try:
                    payload = json.loads(line)
                    if isinstance(payload, dict):
                        records.append(payload)
                except json.JSONDecodeError:
                    continue
        return records

    def count(self) -> int:
        return self._sql_store.count() if self._sql_store is not None else len(self.records())

    def close(self) -> None:
        if self._sql_store is not None:
            self._sql_store.close()


class AdaptiveBrain:
    """Persistent, similarity-based online learner for NIFTY trade patterns."""

    MIN_MATCHES = 8
    MIN_SIMILARITY = 75.0
    MIN_WIN_RATE = 55.0

    def __init__(self, store: BrainStore | None = None):
        self.extractor = FeatureExtractor()
        self.similarity = SimilarityEngine()
        self.memory = MarketMemory()
        self.store = store or BrainStore()
        self._restore_history()

    def _restore_history(self) -> None:
        for payload in self.store.records():
            raw = payload.get("record")
            if not isinstance(raw, dict) or raw.get("outcome") not in {"WIN", "LOSS"}:
                continue
            try:
                fields = {k: v for k, v in raw.items() if k in TradeIntelligenceRecord.__dataclass_fields__}
                if isinstance(fields.get("reasons"), list):
                    fields["reasons"] = list(fields["reasons"])
                self.memory.add(TradeIntelligenceRecord(**fields))
            except (TypeError, ValueError):
                continue

    @staticmethod
    def _trade_id(trade: Any) -> str:
        if trade is None:
            return ""
        return str(getattr(getattr(trade, "order", None), "order_id", "") or getattr(trade, "order_id", "") or "")

    @classmethod
    def _closed_trade(cls, broker: Any = None) -> Any:
        trade = getattr(broker, "last_trade", None) if broker else None
        if trade is None or not getattr(trade, "closed", False):
            return None
        try:
            float(trade.pnl)
        except (TypeError, ValueError):
            return None
        return trade

    def _historical(self) -> list[TradeIntelligenceRecord]:
        return [r for r in self.memory.records if r.outcome in {"WIN", "LOSS"}]

    def evaluate(self, ctx: Any) -> BrainDecision:
        record = self.extractor.extract(ctx)
        historical = self._historical()
        if not record.signal or record.signal == "WAIT":
            return BrainDecision("WAIT", record.signal or "WAIT", 0.0, 0.0, 0.0, 0, 0, 0, "ALLOW", "No actionable NIFTY signal.")
        matches = self.similarity.search(record, historical, top_n=20)
        strong = [(score, item) for score, item in matches if score >= self.MIN_SIMILARITY]
        if not strong:
            return BrainDecision("LEARNING", record.signal, 0.0, 0.0, 0.0, 0, 0, 0, "ALLOW", "No sufficiently similar resolved history yet.")
        weights = [max(score, 1.0) for score, _ in strong]
        total_weight = sum(weights)
        wins = sum(1 for _, item in strong if item.outcome == "WIN")
        losses = sum(1 for _, item in strong if item.outcome == "LOSS")
        weighted_win_rate = sum(weight for weight, (_, item) in zip(weights, strong) if item.outcome == "WIN") / total_weight * 100.0
        average_pnl = sum(float(item.pnl or 0.0) * weight for weight, (_, item) in zip(weights, strong)) / total_weight
        best_similarity = max(score for score, _ in strong)
        if len(strong) < self.MIN_MATCHES:
            return BrainDecision("LEARNING", record.signal, best_similarity, round(weighted_win_rate, 2), round(average_pnl, 2), len(strong), wins, losses, "ALLOW", f"Only {len(strong)}/{self.MIN_MATCHES} strong historical matches.")
        if weighted_win_rate < self.MIN_WIN_RATE or average_pnl <= 0:
            return BrainDecision("VETO", record.signal, best_similarity, round(weighted_win_rate, 2), round(average_pnl, 2), len(strong), wins, losses, "BLOCK", "Similar historical NIFTY setups have not produced a positive edge.")
        return BrainDecision("PASS", record.signal, best_similarity, round(weighted_win_rate, 2), round(average_pnl, 2), len(strong), wins, losses, "ALLOW", "Similar historical NIFTY setups have a positive learned edge.")

    def _pending_record(self, trade_id: str) -> TradeIntelligenceRecord | None:
        if not trade_id:
            return None
        for payload in reversed(self.store.records()):
            if str(payload.get("trade_id") or "") != trade_id:
                continue
            raw = payload.get("record")
            if isinstance(raw, dict) and raw.get("outcome") in {None, ""}:
                try:
                    fields = {k: v for k, v in raw.items() if k in TradeIntelligenceRecord.__dataclass_fields__}
                    if isinstance(fields.get("reasons"), list):
                        fields["reasons"] = list(fields["reasons"])
                    return TradeIntelligenceRecord(**fields)
                except (TypeError, ValueError):
                    return None
        return None

    def _already_learned(self, trade_id: str) -> bool:
        return bool(trade_id) and any(str(payload.get("trade_id") or "") == trade_id and payload.get("outcome") in {"WIN", "LOSS"} for payload in self.store.records())

    def observe(self, ctx: Any, broker: Any = None) -> BrainObservation:
        """Persist entry evidence and resolve it later against the same trade."""
        closed = self._closed_trade(broker)
        if closed is not None:
            trade_id = self._trade_id(closed)
            if trade_id and self._already_learned(trade_id):
                historical = self._historical()
                return BrainObservation("ALREADY_LEARNED", int(getattr(ctx, "cycle_no", 0) or 0), "", 0.0, 0.0, "", True, trade_id, len(historical))
            if trade_id:
                record = self._pending_record(trade_id)
                if record is not None:
                    record.outcome = "WIN" if float(closed.pnl) > 0 else "LOSS"
                    record.pnl = float(closed.pnl)
                    record.exit_price = float(getattr(closed, "exit_price", 0.0) or 0.0)
                    exit_time = getattr(closed, "exit_time", None)
                    entry_time = getattr(getattr(closed, "order", None), "order_time", None)
                    if exit_time is not None and entry_time is not None and hasattr(exit_time, "__sub__"):
                        record.holding_minutes = max(0.0, (exit_time - entry_time).total_seconds() / 60.0)
                    self.memory.add(record)
                    self.store.append({"timestamp": datetime.now(timezone.utc).isoformat(), "cycle_no": int(getattr(ctx, "cycle_no", 0) or 0), "trade_id": trade_id, "outcome": record.outcome, "record": asdict(record), "learning_event": True})
                    historical = self._historical()
                    signal_records = [r for r in historical if r.signal == record.signal]
                    wins = sum(1 for r in signal_records if r.outcome == "WIN")
                    return BrainObservation("LEARNED", int(getattr(ctx, "cycle_no", 0) or 0), record.signal, record.similarity_score, round(wins / len(signal_records) * 100.0, 2) if signal_records else 0.0, record.outcome, True, trade_id, len(historical))

        record = self.extractor.extract(ctx)
        open_position = getattr(broker, "position", None) if broker else None
        trade_id = self._trade_id(open_position)
        if trade_id and not self._already_learned(trade_id) and self._pending_record(trade_id) is None:
            record.trade_id = trade_id
            self.store.append({"timestamp": datetime.now(timezone.utc).isoformat(), "cycle_no": int(getattr(ctx, "cycle_no", 0) or 0), "trade_id": trade_id, "outcome": "", "record": asdict(record), "learning_event": False})
            return BrainObservation("WAITING_OUTCOME", int(getattr(ctx, "cycle_no", 0) or 0), record.signal, 0.0, 0.0, "", True, trade_id, len(self._historical()))

        self.store.append({"timestamp": datetime.now(timezone.utc).isoformat(), "cycle_no": int(getattr(ctx, "cycle_no", 0) or 0), "trade_id": trade_id, "outcome": "", "record": asdict(record), "learning_event": False})
        historical = self._historical()
        signal_records = [r for r in historical if r.signal == record.signal]
        wins = sum(1 for r in signal_records if r.outcome == "WIN")
        return BrainObservation("WAITING_OUTCOME", int(getattr(ctx, "cycle_no", 0) or 0), record.signal, 0.0, round(wins / len(signal_records) * 100.0, 2) if signal_records else 0.0, "", True, trade_id, len(historical))
