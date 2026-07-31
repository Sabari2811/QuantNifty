from dataclasses import dataclass
from datetime import datetime


@dataclass
class RiskState:
    """
    Maintains runtime risk statistics.

    Reset every trading day.
    """

    # Daily Statistics
    trades_today: int = 0
    todays_pnl: float = 0.0

    # Loss Tracking
    consecutive_losses: int = 0

    # Cooldown
    cooldown_until: datetime | None = None

    # Last Reset
    trading_day: datetime | None = None

    def reset(self):

        self.trades_today = 0
        self.todays_pnl = 0.0
        self.consecutive_losses = 0
        self.cooldown_until = None