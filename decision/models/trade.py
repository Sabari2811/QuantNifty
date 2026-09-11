from dataclasses import dataclass, field
from typing import Optional

from .option_contract import OptionContract
from .execution_plan import ExecutionPlan


@dataclass
class Trade:
    """Executable NIFTY option trade."""

    symbol: str = "NIFTY"
    contract: Optional[OptionContract] = None
    option_type: str = ""
    strike: float = 0
    entry: float = 0
    stop_loss: float = 0
    target1: float = 0
    target2: float = 0
    risk_reward: float = 0
    execution: ExecutionPlan = field(default_factory=ExecutionPlan)
