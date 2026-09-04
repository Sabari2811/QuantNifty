from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable


class ReconciliationStatus(str, Enum):
    MATCH = "MATCH"
    MISMATCH = "MISMATCH"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class PositionSnapshot:
    client_order_id: str
    symbol: str
    option_type: str
    strike: float
    quantity: int
    status: str
    broker_order_id: str = ""


@dataclass(frozen=True, slots=True)
class ReconciliationIssue:
    key: str
    reason: str
    local: PositionSnapshot | None = None
    broker: PositionSnapshot | None = None


@dataclass(frozen=True, slots=True)
class ReconciliationReport:
    status: ReconciliationStatus
    local_count: int
    broker_count: int
    issues: tuple[ReconciliationIssue, ...] = field(default_factory=tuple)

    @property
    def safe_to_continue(self) -> bool:
        return self.status is ReconciliationStatus.MATCH


def reconcile_positions(
    local_positions: Iterable[PositionSnapshot] | None,
    broker_positions: Iterable[PositionSnapshot] | None,
) -> ReconciliationReport:
    """Compare canonical local and broker position snapshots without mutation.

    Missing snapshots are UNKNOWN rather than an empty broker state. Matching
    is identity-first and then compares the execution-relevant position shape.
    """
    if local_positions is None or broker_positions is None:
        return ReconciliationReport(
            status=ReconciliationStatus.UNKNOWN,
            local_count=0 if local_positions is None else len(tuple(local_positions)),
            broker_count=0 if broker_positions is None else len(tuple(broker_positions)),
            issues=(ReconciliationIssue("snapshot", "Position snapshot unavailable"),),
        )

    local = tuple(local_positions)
    broker = tuple(broker_positions)
    local_by_id = {p.client_order_id: p for p in local}
    broker_by_id = {p.client_order_id: p for p in broker}
    issues: list[ReconciliationIssue] = []

    for key, position in local_by_id.items():
        counterpart = broker_by_id.get(key)
        if counterpart is None:
            issues.append(ReconciliationIssue(key, "Missing broker position", local=position))
            continue
        if position.symbol != counterpart.symbol:
            issues.append(ReconciliationIssue(key, "Symbol mismatch", local=position, broker=counterpart))
        elif position.option_type != counterpart.option_type:
            issues.append(ReconciliationIssue(key, "Option type mismatch", local=position, broker=counterpart))
        elif position.strike != counterpart.strike:
            issues.append(ReconciliationIssue(key, "Strike mismatch", local=position, broker=counterpart))
        elif position.quantity != counterpart.quantity:
            issues.append(ReconciliationIssue(key, "Quantity mismatch", local=position, broker=counterpart))
        elif position.status != counterpart.status:
            issues.append(ReconciliationIssue(key, "Status mismatch", local=position, broker=counterpart))
        elif position.broker_order_id and counterpart.broker_order_id != position.broker_order_id:
            issues.append(ReconciliationIssue(key, "Broker order ID mismatch", local=position, broker=counterpart))

    for key, position in broker_by_id.items():
        if key not in local_by_id:
            issues.append(ReconciliationIssue(key, "Untracked broker position", broker=position))

    status = ReconciliationStatus.MATCH if not issues else ReconciliationStatus.MISMATCH
    return ReconciliationReport(status, len(local), len(broker), tuple(issues))
