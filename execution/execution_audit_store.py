from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
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
