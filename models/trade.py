from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Trade:

    timestamp: datetime

    symbol: str

    action: str

    option_type: str

    strike: float

    entry: float

    stop_loss: float

    target1: float

    target2: float

    confidence: int

    institutional_score: int

    quantity: int = 0

    status: str = "OPEN"

    exit_price: float = 0.0

    pnl: float = 0.0

    remarks: str = ""

    reasons: list[str] = field(default_factory=list)


    