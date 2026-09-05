from __future__ import annotations

from pathlib import Path

from execution.position_state_store import SQLitePositionStateStore


def build_position_state_store(path: str | Path) -> SQLitePositionStateStore:
    """Create the durable canonical position-state store for a runtime session."""
    return SQLitePositionStateStore(path)
