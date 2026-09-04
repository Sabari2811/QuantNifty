from __future__ import annotations

from dataclasses import dataclass

from execution.execution_contract import ExecutionResult, ExecutionStatus, OrderIntent
from execution.live_indmoney_execution_adapter import LiveINDMoneyExecutionAdapter
from execution.runtime_safety_gate import evaluate_runtime_safety


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
        decision = evaluate_runtime_safety(
            intent=intent,
            kill_switch=self.kill_switch,
            reconciliation_result=reconciliation_result,
            reconciliation_report=reconciliation_report,
        )
        return LiveExecutionRuntimeDecision(
            allowed=decision.allowed,
            reason=decision.reason,
        )

    def execute(
        self,
        *,
        intent: OrderIntent,
        reconciliation_result=None,
        reconciliation_report=None,
    ) -> ExecutionResult:
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
