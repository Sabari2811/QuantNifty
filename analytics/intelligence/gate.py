from __future__ import annotations

from analytics.intelligence.gate_models import (
    IntelligenceGateResult,
)
from analytics.intelligence.result import IntelligenceResult


class IntelligenceGate:
    """
    Structural execution-eligibility gate for Intelligence.

    Responsibilities
    ----------------
    This gate determines whether an IntelligenceResult is structurally
    safe to pass toward the execution layer.

    It does NOT:

    - create trading signals
    - replace DecisionEngine
    - perform portfolio risk validation
    - size positions
    - execute trades
    - introduce strategy thresholds

    Strategy policy and portfolio risk remain owned by their
    authoritative engines.

    Compatibility
    -------------
    If Intelligence is not available, callers may skip this gate
    entirely. This class therefore does not define a policy for
    ``None`` IntelligenceResult.

    Initial C8 policy
    -----------------
    Only explicit data-quality failures block execution:

        invalid   -> BLOCK
        stale     -> BLOCK
        incomplete -> BLOCK

    Otherwise:

        ALLOW

    This deliberately avoids inventing conviction, opportunity,
    regime, or directional thresholds at this stage.
    """

    def evaluate(
        self,
        intelligence: IntelligenceResult,
    ) -> IntelligenceGateResult:
        """
        Evaluate Intelligence execution eligibility.

        Parameters
        ----------
        intelligence:
            Canonical IntelligenceResult produced by IntelligenceService.

        Returns
        -------
        IntelligenceGateResult
            Deterministic ALLOW/BLOCK result.
        """

        if intelligence is None:
            raise ValueError(
                "IntelligenceResult is required."
            )

        data_quality = intelligence.data_quality

        reasons: list[str] = []

        if data_quality.invalid:
            reasons.append(
                "Intelligence data is explicitly invalid."
            )

        if data_quality.stale:
            reasons.append(
                "Intelligence data is explicitly stale."
            )

        if data_quality.incomplete:
            reasons.append(
                "Intelligence data is explicitly incomplete."
            )

        if reasons:
            return IntelligenceGateResult(
                status="BLOCK",
                reason=reasons[0],
                reasons=tuple(reasons),
            )

        return IntelligenceGateResult(
            status="ALLOW",
            reason="Intelligence data quality is acceptable.",
            reasons=(),
        )