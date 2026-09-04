from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class PositionStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class PositionState:
    """Canonical runtime position state used by execution lifecycle logic."""

    client_order_id: str
    broker_order_id: str
    symbol: str
    option_type: str
    strike: float
    quantity: int
    entry_price: float
    current_price: float
    stop_loss: float | None = None
    target: float | None = None
    trailing_stop: float | None = None
    status: PositionStatus = PositionStatus.OPEN
    opened_at: datetime | None = None
    closed_at: datetime | None = None

    def __post_init__(self) -> None:
        if not str(self.client_order_id).strip():
            raise ValueError("client_order_id is required")
        if not str(self.symbol).strip():
            raise ValueError("symbol is required")
        if not str(self.option_type).strip():
            raise ValueError("option_type is required")
        if self.strike <= 0:
            raise ValueError("strike must be positive")
        if self.quantity <= 0:
            raise ValueError("quantity must be positive")
        if self.entry_price < 0:
            raise ValueError("entry_price must be non-negative")
        if self.current_price < 0:
            raise ValueError("current_price must be non-negative")
        if self.stop_loss is not None and self.stop_loss < 0:
            raise ValueError("stop_loss must be non-negative")
        if self.target is not None and self.target < 0:
            raise ValueError("target must be non-negative")
        if self.trailing_stop is not None and self.trailing_stop < 0:
            raise ValueError("trailing_stop must be non-negative")
        if self.status is PositionStatus.CLOSED and self.closed_at is None:
            raise ValueError("closed_at is required for a closed position")
        if self.status is PositionStatus.OPEN and self.closed_at is not None:
            raise ValueError("closed_at is not allowed for an open position")
