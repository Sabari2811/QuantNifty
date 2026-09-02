from dataclasses import dataclass, field

from .signal import Signal
from .trade import Trade
from .market import Market
from decision.validation_result import ValidationResult


@dataclass
class Decision:
    """
    Final output of Decision Engine.

    The authoritative market snapshot is preserved by identity
    so downstream execution and audit layers can trace the
    decision back to the exact snapshot used for analysis.

    Strategy identity is also preserved explicitly so downstream
    intelligence layers do not need to infer it from the
    Python strategy class name.

    The pre-execution signal is preserved separately because
    execution preparation/validation may legitimately change
    ``signal.name`` to WAIT when a trade cannot be executed.
    Audit and reconciliation layers must compare Intelligence
    against this authoritative pre-execution decision, not the
    post-validation execution state.
    """

    # ------------------------------------------------------------------
    # Authoritative source snapshot
    # ------------------------------------------------------------------

    snapshot: object = None

    # ------------------------------------------------------------------
    # Authoritative strategy identity
    # ------------------------------------------------------------------

    strategy_name: str = ""

    # ------------------------------------------------------------------
    # Authoritative pre-execution signal
    # ------------------------------------------------------------------

    authoritative_signal: str = ""

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
