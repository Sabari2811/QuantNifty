from dataclasses import dataclass


@dataclass
class Signal:
    """
    Trading signal produced by the Decision Engine.
    """

    name: str = "WAIT"

    confidence: int = 0