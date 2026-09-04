from __future__ import annotations

from dataclasses import dataclass

from execution.execution_contract import ExecutionResult, ExecutionStatus, OrderIntent
from execution.kill_switch import KillSwitch


@dataclass(frozen=True, slots=True)
class KillSwitchGateDecision:
    allowed: bool
    reason: str


def evaluate_kill_switch_gate(
    switch: KillSwitch | None,
    intent: OrderIntent | None,
) -> KillSwitchGateDecision:
    """Fail closed when an execution intent is present and the kill switch is active."""
    if intent is None:
        return KillSwitchGateDecision(True, "No execution intent; kill switch gate not applicable.")
    if switch is None:
        return KillSwitchGateDecision(False, "Kill switch state is unavailable; execution is blocked.")
    allowed, reason = switch.check()
    if allowed:
        return KillSwitchGateDecision(True, reason)
    return KillSwitchGateDecision(False, f"Kill switch active: {reason}")


def rejected_result(intent: OrderIntent, decision: KillSwitchGateDecision) -> ExecutionResult:
    return ExecutionResult(
        status=ExecutionStatus.REJECTED,
        intent=intent,
        reason=decision.reason,
    )
