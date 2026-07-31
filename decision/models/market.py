from dataclasses import dataclass


@dataclass
class Market:
    """
    Market summary used by the Decision Engine.
    """

    dealer: str = ""

    institutional: str = ""

    probability: float = 0