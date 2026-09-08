"""Optional SQL-backed append-only persistence for runtime evidence.

The application keeps JSONL as the deterministic local fallback. Production
services can opt into SQL durability by supplying a dedicated database URL.
The store never silently falls back when a database URL is explicitly set.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Column, DateTime, Integer, MetaData, Table, Text, create_engine, select, func


class SqlAppendStore:
    """Append-only JSON payload store backed by SQLAlchemy."""

    def __init__(self, database_url: str, table_name: str):
        if not database_url:
            raise ValueError("database_url is required")
        self.engine = create_engine(database_url, pool_pre_ping=True)
        self.metadata = MetaData()
        self.table = Table(
            table_name,
            self.metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("created_at", DateTime(timezone=True), nullable=False),
            Column("payload", Text, nullable=False),
        )
        self.metadata.create_all(self.engine)

    def append(self, record: Any) -> None:
        payload = record if isinstance(record, dict) else dict(record)
        with self.engine.begin() as connection:
            connection.execute(
                self.table.insert().values(
                    created_at=datetime.now(timezone.utc),
                    payload=json.dumps(payload, default=str, sort_keys=True),
                )
            )

    def records(self) -> list[dict[str, Any]]:
        with self.engine.connect() as connection:
            rows = connection.execute(
                select(self.table.c.payload).order_by(self.table.c.id.asc())
            ).scalars().all()
        result: list[dict[str, Any]] = []
        for raw in rows:
            try:
                value = json.loads(raw)
            except (TypeError, ValueError):
                continue
            if isinstance(value, dict):
                result.append(value)
        return result

    def count(self) -> int:
        with self.engine.connect() as connection:
            value = connection.execute(select(func.count()).select_from(self.table)).scalar_one()
        return int(value)

    def close(self) -> None:
        self.engine.dispose()
