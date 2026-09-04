from __future__ import annotations

from dataclasses import dataclass

from execution.kill_switch_gate import evaluate_kill_switch_gate
from execution.reconciliation_runtime_gate import evaluate_runtime_reconciliation_gate
from execution.reconciliation import ReconciliationReport
from execution.execution_contract import OrderIntent


@dataclass(frozen=True, slots=True)
class RuntimeSafetyDecision:
    allowed: bool
    reason: str


def evaluate_runtime_safety(
    *,
    intent: OrderIntent | None,
    kill_switch,
    reconciliation_report: ReconciliationReport | None = None,
    reconciliation_required: bool = False,
) -> RuntimeSafetyDecision:
    """Compose fail-closed execution safety controls without broker calls."""
    kill = evaluate_kill_switch_gate(kill_switch, intent)
    if not kill.allowed:
        return RuntimeSafetyDecision(False, kill.reason)

    if reconciliation_required:
        reconciliation = evaluate_runtime_reconciliation_gate(reconciliation_report)
        if not reconciliation.allowed:
            return RuntimeSafetyDecision(False, reconciliation.reason)

    return RuntimeSafetyDecision(True, "Runtime execution safety gates passed.")
