from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


GateStatus = Literal[
    "ALLOW",
    "BLOCK",
]


@dataclass(frozen=True, slots=True)
class IntelligenceGateResult:
    """
    Result of the Intelligence execution-eligibility gate.

    The gate does not create or modify a trading decision.
    It only determines whether the existing decision may proceed
    to the execution layer.
    """

    status: GateStatus

    reason: str = ""

    reasons: tuple[str, ...] = ()

    @property
    def allowed(self) -> bool:
        """Return True when Intelligence permits execution."""
        return self.status == "ALLOW"

    @property
    def blocked(self) -> bool:
        """Return True when Intelligence blocks execution."""
        return self.status == "BLOCK"