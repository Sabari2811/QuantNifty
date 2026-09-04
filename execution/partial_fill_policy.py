from __future__ import annotations

from dataclasses import dataclass

from execution.execution_contract import ExecutionResult, ExecutionStatus


@dataclass(frozen=True, slots=True)
class PartialFillDecision:
    complete: bool
    follow_up_required: bool
    reason: str


def evaluate_partial_fill(result: ExecutionResult) -> PartialFillDecision:
    """Classify fill quantity without inventing a broker lifecycle state."""
    if result.status is not ExecutionStatus.EXECUTED:
        return PartialFillDecision(False, False, "Partial-fill evaluation applies only to EXECUTED results.")

    quantity = result.intent.quantity
    filled = result.filled_quantity

    if filled < 0 or filled > quantity:
        return PartialFillDecision(False, True, "Filled quantity is outside the requested quantity range.")
    if filled == quantity:
        return PartialFillDecision(True, False, "Requested quantity is fully filled.")
    if filled == 0:
        return PartialFillDecision(False, True, "Execution result reports no filled quantity; broker state requires reconciliation.")
    return PartialFillDecision(False, True, "Execution result is partially filled; remaining broker state requires explicit lifecycle handling.")
