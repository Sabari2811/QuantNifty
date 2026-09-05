from __future__ import annotations

import sqlite3
from datetime import datetime

from execution.position_state import PositionState, PositionStatus


class SQLitePositionStateStore:
    """Durable store for the canonical PositionState boundary."""

    def __init__(self, path: str):
        self._connection = sqlite3.connect(path)
        self._connection.execute("PRAGMA journal_mode=WAL")
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS position_state (
                client_order_id TEXT PRIMARY KEY,
                broker_order_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                option_type TEXT NOT NULL,
                strike REAL NOT NULL,
                quantity INTEGER NOT NULL,
                entry_price REAL NOT NULL,
                current_price REAL NOT NULL,
                stop_loss REAL,
                target REAL,
                trailing_stop REAL,
                status TEXT NOT NULL,
                opened_at TEXT,
                closed_at TEXT
            )
            """
        )
        self._connection.commit()

    def save(self, position: PositionState) -> PositionState:
        self._connection.execute(
            """
            INSERT INTO position_state (
                client_order_id, broker_order_id, symbol, option_type, strike,
                quantity, entry_price, current_price, stop_loss, target,
                trailing_stop, status, opened_at, closed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(client_order_id) DO UPDATE SET
                broker_order_id=excluded.broker_order_id,
                symbol=excluded.symbol,
                option_type=excluded.option_type,
                strike=excluded.strike,
                quantity=excluded.quantity,
                entry_price=excluded.entry_price,
                current_price=excluded.current_price,
                stop_loss=excluded.stop_loss,
                target=excluded.target,
                trailing_stop=excluded.trailing_stop,
                status=excluded.status,
                opened_at=excluded.opened_at,
                closed_at=excluded.closed_at
            """,
            self._row(position),
        )
        self._connection.commit()
        return position

    def get(self, client_order_id: str) -> PositionState | None:
        row = self._connection.execute(
            "SELECT * FROM position_state WHERE client_order_id = ?",
            (str(client_order_id).strip(),),
        ).fetchone()
        return None if row is None else self._from_row(row)

    def open_positions(self) -> tuple[PositionState, ...]:
        rows = self._connection.execute(
            "SELECT * FROM position_state WHERE status = ? ORDER BY client_order_id",
            (PositionStatus.OPEN.value,),
        ).fetchall()
        return tuple(self._from_row(row) for row in rows)

    def close(self) -> None:
        self._connection.close()

    def __enter__(self) -> "SQLitePositionStateStore":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    @staticmethod
    def _row(position: PositionState) -> tuple:
        return (
            position.client_order_id,
            position.broker_order_id,
            position.symbol,
            position.option_type,
            position.strike,
            position.quantity,
            position.entry_price,
            position.current_price,
            position.stop_loss,
            position.target,
            position.trailing_stop,
            position.status.value,
            position.opened_at.isoformat() if position.opened_at else None,
            position.closed_at.isoformat() if position.closed_at else None,
        )

    @staticmethod
    def _from_row(row: tuple) -> PositionState:
        return PositionState(
            client_order_id=row[0],
            broker_order_id=row[1],
            symbol=row[2],
            option_type=row[3],
            strike=row[4],
            quantity=row[5],
            entry_price=row[6],
            current_price=row[7],
            stop_loss=row[8],
            target=row[9],
            trailing_stop=row[10],
            status=PositionStatus(row[11]),
            opened_at=_parse_datetime(row[12]),
            closed_at=_parse_datetime(row[13]),
        )


def _parse_datetime(value: str | None) -> datetime | None:
    return None if value is None else datetime.fromisoformat(value)
