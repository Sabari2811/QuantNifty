from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ExecutionAction(str, Enum):
    """Canonical action requested at the execution boundary."""

    BUY = "BUY"
    SELL = "SELL"


class ExecutionStatus(str, Enum):
    """Canonical outcome of an execution attempt."""

    NOT_SUBMITTED = "NOT_SUBMITTED"
    SUBMITTED = "SUBMITTED"
    EXECUTED = "EXECUTED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class OrderIntent:
    """Canonical, broker-neutral request produced before execution."""

    symbol: str
    option_type: str
    strike: float
    action: ExecutionAction
    quantity: int
    limit_price: float
    strategy_name: str = ""
    source: str = "decision"
    client_order_id: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.symbol.strip():
            raise ValueError("OrderIntent.symbol must be non-empty")
        if not self.option_type.strip():
            raise ValueError("OrderIntent.option_type must be non-empty")
        if self.strike <= 0:
            raise ValueError("OrderIntent.strike must be positive")
        if self.quantity <= 0:
            raise ValueError("OrderIntent.quantity must be positive")
        if self.limit_price < 0:
            raise ValueError("OrderIntent.limit_price must be non-negative")


@dataclass(frozen=True, slots=True)
class ExecutionResult:
    """Canonical broker outcome; never inferred from local state alone."""

    status: ExecutionStatus
    intent: OrderIntent
    broker_order_id: str = ""
    filled_quantity: int = 0
    average_fill_price: float | None = None
    reason: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    raw: Any = None

    @property
    def successful(self) -> bool:
        return self.status is ExecutionStatus.EXECUTED

    @property
    def terminal(self) -> bool:
        return self.status in {
            ExecutionStatus.EXECUTED,
            ExecutionStatus.REJECTED,
            ExecutionStatus.FAILED,
        }
