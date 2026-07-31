from dataclasses import dataclass, field
from typing import Optional

from .option_contract import OptionContract
from .execution_plan import ExecutionPlan


@dataclass
class Trade:
    """
    Represents the executable option trade.

    This contains:
    - Selected option contract
    - Trade details
    - Execution plan
    """

    # =====================================================
    # Selected Contract
    # =====================================================

    contract: Optional[OptionContract] = None

    # =====================================================
    # Option Details
    # =====================================================

    option_type: str = ""

    strike: float = 0

    # =====================================================
    # Premium Trade
    # =====================================================

    entry: float = 0

    stop_loss: float = 0

    target1: float = 0

    target2: float = 0

    risk_reward: float = 0

    # =====================================================
    # Execution Plan
    # =====================================================

    execution: ExecutionPlan = field(
        default_factory=ExecutionPlan
    )