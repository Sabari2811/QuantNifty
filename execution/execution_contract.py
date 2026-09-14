from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ExecutionAction(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class ExecutionStatus(str, Enum):
    CREATED = "CREATED"
    SUBMITTED = "SUBMITTED"
    EXECUTED = "EXECUTED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    UNKNOWN = "UNKNOWN"
    FAILED = "FAILED"


@dataclass(frozen=True)
class OrderIntent:
    symbol: str
    option_type: str
    strike: float
    action: ExecutionAction
    quantity: int
    limit_price: Optional[float] = None
    strategy_name: str = ""
    client_order_id: str = ""

    def __post_init__(self):
        if not self.client_order_id:
            raise ValueError("client_order_id is required")
        if self.symbol != "NIFTY":
            raise ValueError("Execution contract is NIFTY-only")
        if self.quantity <= 0:
            raise ValueError("quantity must be positive")


@dataclass(frozen=True)
class ExecutionResult:
    status: ExecutionStatus
    intent: OrderIntent
    broker_order_id: Optional[str] = None
    filled_quantity: int = 0
    average_fill_price: Optional[float] = None
    reason: str = ""
    metadata: dict = field(default_factory=dict)

    @property
    def terminal(self) -> bool:
        return self.status in {
            ExecutionStatus.EXECUTED,
            ExecutionStatus.REJECTED,
            ExecutionStatus.CANCELLED,
            ExecutionStatus.FAILED,
        }

    @property
    def ambiguous(self) -> bool:
        return self.status in {
            ExecutionStatus.SUBMITTED,
            ExecutionStatus.UNKNOWN,
        }
