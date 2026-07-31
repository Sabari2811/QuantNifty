from dataclasses import dataclass


@dataclass
class OptionContract:
    """
    Represents one tradable option contract.
    """

    strike: int

    option_type: str

    expiry: str = ""

    ltp: float = 0.0

    bid: float = 0.0

    ask: float = 0.0

    volume: int = 0

    oi: int = 0

    iv: float = 0.0

    delta: float = 0.0

    gamma: float = 0.0

    theta: float = 0.0

    vega: float = 0.0