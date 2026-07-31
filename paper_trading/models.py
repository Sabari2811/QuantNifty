from dataclasses import dataclass, field
from datetime import datetime


# ==========================================================
# Order
# ==========================================================

@dataclass
class PaperOrder:

    order_id: str

    signal: str

    option_type: str

    strike: int

    quantity: int

    entry_price: float

    order_time: datetime = field(default_factory=datetime.now)

    status: str = "OPEN"


# ==========================================================
# Position (Live Trade)
# ==========================================================

@dataclass
class PaperPosition:

    order: PaperOrder

    current_price: float = 0.0

    stop_loss: float = 0.0

    target: float = 0.0

    pnl: float = 0.0

    closed: bool = False

    exit_price: float = 0.0

    exit_time: datetime | None = None

    # Runtime Metadata
    confidence: float = 0.0

    risk_reward: float = 0.0

    strategy_name: str = ""

    entry_candle: int = 0

    exit_candle: int = 0


# ==========================================================
# Portfolio
# ==========================================================

@dataclass
class Portfolio:

    capital: float = 500000

    available_cash: float = 500000

    invested_amount: float = 0

    realized_pnl: float = 0

    unrealized_pnl: float = 0

    open_positions: list = field(default_factory=list)

    closed_positions: list = field(default_factory=list)


# ==========================================================
# Trade Journal Record
# ==========================================================

@dataclass(frozen=True)
class TradeRecord:

    # ==============================================
    # Identity
    # ==============================================

    order_id: str

    strategy_name: str

    signal: str

    option_type: str

    strike: int

    quantity: int

    # ==============================================
    # Prices
    # ==============================================

    entry_price: float

    exit_price: float

    pnl: float

    # ==============================================
    # Time
    # ==============================================

    entry_time: datetime

    exit_time: datetime

    holding_seconds: float

    # ==============================================
    # Risk
    # ==============================================

    confidence: float

    risk_reward: float

    probability: float = 0.0

    # ==============================================
    # Market Context
    # ==============================================

    regime: str = ""

    dealer_position: str = ""

    # ==============================================
    # Replay
    # ==============================================

    entry_candle: int = 0

    exit_candle: int = 0

    exit_reason: str = ""