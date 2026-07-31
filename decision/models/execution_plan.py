from dataclasses import dataclass


@dataclass
class ExecutionPlan:
    """
    Final executable trade plan.
    """

    capital: float = 0

    risk_percent: float = 0

    risk_amount: float = 0

    lot_size: int = 0

    lots: int = 0

    premium_entry: float = 0

    premium_stop_loss: float = 0

    premium_target1: float = 0

    premium_target2: float = 0

    risk_reward: float = 0

    trade_quality: int = 0