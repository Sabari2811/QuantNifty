from __future__ import annotations

from pathlib import Path

from execution.execution_audit_store import SQLiteExecutionAuditStore


def build_runtime_audit_store(path: str | Path) -> SQLiteExecutionAuditStore:
    """Create the durable execution audit store for a runtime session."""
    return SQLiteExecutionAuditStore(path)
