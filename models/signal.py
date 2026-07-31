from dataclasses import dataclass


@dataclass
class Signal:

    action: str

    confidence: int

    score: int

    regime: str

    probability: float

    reasons: list[str]