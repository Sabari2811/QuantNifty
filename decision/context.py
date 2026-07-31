from dataclasses import dataclass, field
from typing import Any


@dataclass
class DecisionContext:

    # --------------------------------------------------
    # Input
    # --------------------------------------------------

    snapshot: Any = None

    # --------------------------------------------------
    # Analytics
    # --------------------------------------------------

    dealer: dict = field(default_factory=dict)

    dealer_flow: dict = field(default_factory=dict)

    pcr: dict = field(default_factory=dict)

    max_pain: dict = field(default_factory=dict)

    gamma: dict = field(default_factory=dict)

    probability: dict = field(default_factory=dict)

    institutional: dict = field(default_factory=dict)

    liquidity: dict = field(default_factory=dict)

    # --------------------------------------------------
    # Decision
    # --------------------------------------------------

    signal: str = "WAIT"

    confidence: int = 0

    reasons: list[str] = field(default_factory=list)

    # --------------------------------------------------
    # Trade
    # --------------------------------------------------

    option_type: str = ""

    strike: float | None = None

    entry: float | None = None

    stop_loss: float | None = None

    target1: float | None = None

    target2: float | None = None

    risk_reward: float | None = None