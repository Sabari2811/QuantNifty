from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Position:
    """
    Represents an active paper trading position.
    """

    position_id: str = ""

    symbol: str = ""

    option_type: str = ""

    strike: float = 0

    quantity: int = 0

    lots: int = 0

    entry_price: float = 0

    current_price: float = 0

    stop_loss: float = 0

    target1: float = 0

    target2: float = 0

    pnl: float = 0

    status: str = "OPEN"

    opened_at: datetime = field(default_factory=datetime.now)