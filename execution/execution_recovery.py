from __future__ import annotations

from dataclasses import dataclass
from execution.execution_audit_store import ExecutionAuditRecord, InMemoryExecutionAuditStore


@dataclass(frozen=True, slots=True)
class RecoveryDecision:
    safe_to_continue: bool
    requires_reconciliation: bool
    requires_manual_resolution: bool
    reason: str


def evaluate_recovery(record: ExecutionAuditRecord | None) -> RecoveryDecision:
    """Restore persisted execution state without inferring broker state."""
    if record is None:
        return RecoveryDecision(False, False, False, "No persisted execution record available.")

    if record.status in {"SUBMITTED", "UNKNOWN"}:
        return RecoveryDecision(
            False,
            True,
            False,
            "Persisted execution outcome is ambiguous; broker reconciliation is required before continuation.",
        )

    if record.status == "EXECUTED":
        return RecoveryDecision(True, False, False, "Persisted execution outcome is terminal and executed.")

    if record.status in {"REJECTED", "FAILED"}:
        return RecoveryDecision(False, False, True, "Persisted execution outcome is terminal but not safe to resume automatically.")

    return RecoveryDecision(False, False, True, f"Unsupported persisted execution status: {record.status}")


def recover_pending(store: InMemoryExecutionAuditStore) -> tuple[ExecutionAuditRecord, ...]:
    """Return only ambiguous persisted executions requiring reconciliation."""
    return store.load_pending()
