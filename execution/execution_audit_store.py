from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

from execution.execution_contract import ExecutionResult, OrderIntent


@dataclass(frozen=True, slots=True)
class ExecutionAuditRecord:
    """Immutable execution audit record suitable for durable persistence."""

    client_order_id: str
    symbol: str
    option_type: str
    strike: float
    quantity: int
    action: str
    limit_price: float
    strategy_name: str
    source: str
    broker_order_id: str
    status: str
    filled_quantity: int
    average_fill_price: float | None
    reason: str
    intent_created_at: datetime
    result_timestamp: datetime

    @classmethod
    def from_result(cls, result: ExecutionResult) -> "ExecutionAuditRecord":
        intent: OrderIntent = result.intent
        if not intent.client_order_id:
            raise ValueError("Execution audit requires client_order_id")
        return cls(
            client_order_id=intent.client_order_id,
            symbol=intent.symbol,
            option_type=intent.option_type,
            strike=intent.strike,
            quantity=intent.quantity,
            action=intent.action.value,
            limit_price=intent.limit_price,
            strategy_name=intent.strategy_name,
            source=intent.source,
            broker_order_id=result.broker_order_id,
            status=result.status.value,
            filled_quantity=result.filled_quantity,
            average_fill_price=result.average_fill_price,
            reason=result.reason,
            intent_created_at=intent.created_at,
            result_timestamp=result.timestamp,
        )


class InMemoryExecutionAuditStore:
    """Reference store defining the persistence boundary used by runtime code.

    The interface is intentionally append-only and keyed by canonical client
    order identity. A durable implementation can replace this store later
    without changing execution contracts.
    """

    def __init__(self) -> None:
        self._records: dict[str, ExecutionAuditRecord] = {}

    def append(self, record: ExecutionAuditRecord) -> None:
        if not record.client_order_id:
            raise ValueError("client_order_id is required")
        existing = self._records.get(record.client_order_id)
        if existing is not None and existing != record:
            raise ValueError("Execution audit record already exists for client_order_id")
        self._records[record.client_order_id] = record

    def get(self, client_order_id: str) -> ExecutionAuditRecord | None:
        return self._records.get(str(client_order_id).strip())

    def records(self) -> tuple[ExecutionAuditRecord, ...]:
        return tuple(self._records.values())

    def load_pending(self) -> tuple[ExecutionAuditRecord, ...]:
        return tuple(
            record
            for record in self._records.values()
            if record.status in {"SUBMITTED", "UNKNOWN"}
        )


class SQLiteExecutionAuditStore:
    """Durable append-only execution audit store backed by SQLite."""

    _COLUMNS = (
        "client_order_id", "symbol", "option_type", "strike", "quantity",
        "action", "limit_price", "strategy_name", "source", "broker_order_id",
        "status", "filled_quantity", "average_fill_price", "reason",
        "intent_created_at", "result_timestamp",
    )

    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(self.path)
        self._connection.execute("PRAGMA journal_mode=WAL")
        self._connection.execute(
            """CREATE TABLE IF NOT EXISTS execution_audit (
                client_order_id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                option_type TEXT NOT NULL,
                strike REAL NOT NULL,
                quantity INTEGER NOT NULL,
                action TEXT NOT NULL,
                limit_price REAL NOT NULL,
                strategy_name TEXT NOT NULL,
                source TEXT NOT NULL,
                broker_order_id TEXT NOT NULL,
                status TEXT NOT NULL,
                filled_quantity INTEGER NOT NULL,
                average_fill_price REAL,
                reason TEXT NOT NULL,
                intent_created_at TEXT NOT NULL,
                result_timestamp TEXT NOT NULL
            )"""
        )
        self._connection.commit()

    @staticmethod
    def _row(record: ExecutionAuditRecord) -> tuple[object, ...]:
        return (
            record.client_order_id, record.symbol, record.option_type, record.strike,
            record.quantity, record.action, record.limit_price, record.strategy_name,
            record.source, record.broker_order_id, record.status, record.filled_quantity,
            record.average_fill_price, record.reason, record.intent_created_at.isoformat(),
            record.result_timestamp.isoformat(),
        )

    @classmethod
    def _record_from_row(cls, row: tuple[object, ...]) -> ExecutionAuditRecord:
        values = dict(zip(cls._COLUMNS, row))
        return ExecutionAuditRecord(
            client_order_id=str(values["client_order_id"]),
            symbol=str(values["symbol"]),
            option_type=str(values["option_type"]),
            strike=float(values["strike"]),
            quantity=int(values["quantity"]),
            action=str(values["action"]),
            limit_price=float(values["limit_price"]),
            strategy_name=str(values["strategy_name"]),
            source=str(values["source"]),
            broker_order_id=str(values["broker_order_id"]),
            status=str(values["status"]),
            filled_quantity=int(values["filled_quantity"]),
            average_fill_price=(
                None if values["average_fill_price"] is None
                else float(values["average_fill_price"])
            ),
            reason=str(values["reason"]),
            intent_created_at=datetime.fromisoformat(str(values["intent_created_at"])),
            result_timestamp=datetime.fromisoformat(str(values["result_timestamp"])),
        )

    def append(self, record: ExecutionAuditRecord) -> None:
        if not record.client_order_id:
            raise ValueError("client_order_id is required")
        existing = self.get(record.client_order_id)
        if existing is not None:
            if existing != record:
                raise ValueError("Execution audit record already exists for client_order_id")
            return
        placeholders = ", ".join("?" for _ in self._COLUMNS)
        columns = ", ".join(self._COLUMNS)
        self._connection.execute(
            f"INSERT INTO execution_audit ({columns}) VALUES ({placeholders})",
            self._row(record),
        )
        self._connection.commit()

    def get(self, client_order_id: str) -> ExecutionAuditRecord | None:
        cursor = self._connection.execute(
            "SELECT " + ", ".join(self._COLUMNS)
            + " FROM execution_audit WHERE client_order_id = ?",
            (str(client_order_id).strip(),),
        )
        row = cursor.fetchone()
        return None if row is None else self._record_from_row(row)

    def records(self) -> tuple[ExecutionAuditRecord, ...]:
        cursor = self._connection.execute(
            "SELECT " + ", ".join(self._COLUMNS)
            + " FROM execution_audit ORDER BY rowid"
        )
        return tuple(self._record_from_row(row) for row in cursor.fetchall())

    def load_pending(self) -> tuple[ExecutionAuditRecord, ...]:
        cursor = self._connection.execute(
            "SELECT " + ", ".join(self._COLUMNS)
            + " FROM execution_audit WHERE status IN ('SUBMITTED', 'UNKNOWN') ORDER BY rowid"
        )
        return tuple(self._record_from_row(row) for row in cursor.fetchall())

    def close(self) -> None:
        self._connection.close()

    def __enter__(self) -> "SQLiteExecutionAuditStore":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()
