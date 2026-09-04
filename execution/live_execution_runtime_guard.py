from __future__ import annotations

from dataclasses import dataclass

from execution.execution_contract import ExecutionResult, ExecutionStatus, OrderIntent
from execution.live_indmoney_execution_adapter import LiveINDMoneyExecutionAdapter
from execution.kill_switch_gate import evaluate_kill_switch_gate
from execution.reconciliation_runtime_gate import evaluate_runtime_reconciliation


@dataclass(frozen=True, slots=True)
class LiveExecutionRuntimeDecision:
    """Decision at the live broker boundary before an order can be submitted."""

    allowed: bool
    reason: str


class LiveExecutionRuntimeGuard:
    """Fail-closed runtime guard for the live execution adapter.

    The guard deliberately owns no market-data or broker-state discovery. It
    evaluates the already-established safety gates and only delegates to the
    provider adapter when execution is explicitly allowed.
    """

    def __init__(self, adapter: LiveINDMoneyExecutionAdapter, kill_switch):
        if adapter is None:
            raise ValueError("Live execution adapter is required")
        if kill_switch is None:
            raise ValueError("Kill switch is required")
        self.adapter = adapter
        self.kill_switch = kill_switch

    def evaluate(
        self,
        *,
        intent: OrderIntent | None,
        reconciliation_result=None,
        reconciliation_report=None,
    ) -> LiveExecutionRuntimeDecision:
        kill = evaluate_kill_switch_gate(self.kill_switch, intent)
        if not kill.allowed:
            return LiveExecutionRuntimeDecision(False, kill.reason)

        if reconciliation_result is not None:
            reconciliation = evaluate_runtime_reconciliation(
                reconciliation_result,
                reconciliation_report,
            )
            if not reconciliation.safe_to_continue:
                return LiveExecutionRuntimeDecision(False, reconciliation.reason)

        return LiveExecutionRuntimeDecision(True, "Live execution runtime gates passed.")

    def execute(
        self,
        *,
        intent: OrderIntent,
        reconciliation_result=None,
        reconciliation_report=None,
    ) -> ExecutionResult:
        if intent is None:
            return ExecutionResult(
                status=ExecutionStatus.REJECTED,
                intent=intent,
                reason="Order intent is required",
            )

        decision = self.evaluate(
            intent=intent,
            reconciliation_result=reconciliation_result,
            reconciliation_report=reconciliation_report,
        )
        if not decision.allowed:
            return ExecutionResult(
                status=ExecutionStatus.REJECTED,
                intent=intent,
                reason=decision.reason,
            )
        return self.adapter.execute(intent)
