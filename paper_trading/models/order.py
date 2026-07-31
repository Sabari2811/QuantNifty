from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class PaperOrder:
    """
    Represents a broker order in paper trading.

    An Order is only a request to buy/sell.
    It may later become a Position.
    """

    order_id: str = ""

    symbol: str = ""

    option_type: str = ""

    strike: float = 0

    side: str = ""

    quantity: int = 0

    lots: int = 0

    price: float = 0

    status: str = "PENDING"

    remarks: str = ""

    timestamp: datetime = field(default_factory=datetime.now)