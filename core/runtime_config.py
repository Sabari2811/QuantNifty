from dataclasses import dataclass


@dataclass
class RuntimeConfig:
    """
    Runtime/session configuration.

    These values change depending on the
    trading account or execution mode.
    """

    capital: float = 500000

    risk_percent: float = 1.0

    default_lot_size: int = 65

    broker: str = "INDMoney"

    paper_mode: bool = True

    live_mode: bool = False