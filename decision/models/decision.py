from dataclasses import dataclass, field

from .signal import Signal
from .trade import Trade
from .market import Market
from decision.validation_result import ValidationResult


@dataclass
class Decision:
    """
    Final output of Decision Engine.
    """

    signal: Signal = field(
        default_factory=Signal
    )

    trade: Trade = field(
        default_factory=Trade
    )

    market: Market = field(
        default_factory=Market
    )

    reasons: list = field(
        default_factory=list
    )

    # Institutional Score Breakdown
    score: dict = field(
        default_factory=dict
    )

    # ------------------------------------------------------------------
    # Legacy field (keep until all modules migrate)
    # ------------------------------------------------------------------
    valid: bool = False

    # ------------------------------------------------------------------
    # New validation model
    # ------------------------------------------------------------------
    validation: ValidationResult = field(
        default_factory=lambda: ValidationResult(
            valid=False,
            grade="F",
            confidence=0,
            risk_multiplier=0.0,
            warnings=[]
        )
    )