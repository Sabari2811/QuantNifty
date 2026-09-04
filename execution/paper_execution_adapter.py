from __future__ import annotations

from execution.execution_contract import (
    ExecutionResult,
    ExecutionStatus,
    OrderIntent,
)


class PaperExecutionAdapter:
    """Broker-neutral adapter for the existing paper broker."""

    def __init__(self, broker):
        self.broker = broker

    def execute(self, intent: OrderIntent, decision) -> ExecutionResult:
        if not intent.client_order_id:
            return ExecutionResult(
                status=ExecutionStatus.REJECTED,
                intent=intent,
                reason="client_order_id is required",
            )

        position = self.broker.execute(decision)
        if position is None:
            return ExecutionResult(
                status=ExecutionStatus.REJECTED,
                intent=intent,
                reason="Paper broker rejected execution",
            )

        return ExecutionResult(
            status=ExecutionStatus.EXECUTED,
            intent=intent,
            broker_order_id=str(getattr(getattr(position, "order", None), "order_id", "")),
            filled_quantity=int(intent.quantity),
            average_fill_price=float(intent.limit_price),
        )
