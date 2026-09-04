from __future__ import annotations

from dataclasses import dataclass

from execution.execution_contract import ExecutionResult, OrderIntent
from execution.kill_switch_gate import evaluate_kill_switch_gate
from execution.reconciliation import ReconciliationReport
from execution.reconciliation_runtime_gate import evaluate_runtime_reconciliation


@dataclass(frozen=True, slots=True)
class RuntimeSafetyDecision:
    allowed: bool
    reason: str


def evaluate_runtime_safety(
    *,
    intent: OrderIntent | None,
    kill_switch,
    reconciliation_result: ExecutionResult | None = None,
    reconciliation_report: ReconciliationReport | None = None,
) -> RuntimeSafetyDecision:
    """Compose fail-closed execution safety controls without broker calls."""
    kill = evaluate_kill_switch_gate(kill_switch, intent)
    if not kill.allowed:
        return RuntimeSafetyDecision(False, kill.reason)

    if reconciliation_result is not None:
        reconciliation = evaluate_runtime_reconciliation(
            reconciliation_result,
            reconciliation_report,
        )
        if not reconciliation.safe_to_continue:
            return RuntimeSafetyDecision(False, reconciliation.reason)

    return RuntimeSafetyDecision(True, "Runtime execution safety gates passed.")
