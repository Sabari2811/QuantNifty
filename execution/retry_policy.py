from __future__ import annotations

from dataclasses import dataclass

from execution.execution_contract import ExecutionResult, ExecutionStatus
from execution.execution_lifecycle import ExecutionLifecycleAction, classify_execution_result


@dataclass(frozen=True, slots=True)
class RetryDecision:
    allowed: bool
    reason: str


def evaluate_retry(result: ExecutionResult, *, retry_count: int = 0, max_retries: int = 0) -> RetryDecision:
    """Decide whether an execution may be retried without inferring broker state."""
    if retry_count < 0 or max_retries < 0:
        raise ValueError("retry counts must be non-negative")

    action = classify_execution_result(result)
    if action is ExecutionLifecycleAction.RECONCILE:
        return RetryDecision(False, "Execution outcome requires reconciliation before retry.")
    if action is not ExecutionLifecycleAction.DO_NOT_RETRY:
        return RetryDecision(False, "Execution result is not retry-eligible.")
    if result.status is ExecutionStatus.REJECTED:
        return RetryDecision(False, "Rejected execution is not automatically retried.")
    if result.status is ExecutionStatus.FAILED and retry_count < max_retries:
        return RetryDecision(True, "Failed execution may be retried within the configured limit.")
    return RetryDecision(False, "Retry limit reached or execution status is not retry-eligible.")
