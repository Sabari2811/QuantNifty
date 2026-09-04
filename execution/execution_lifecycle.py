from __future__ import annotations

from enum import Enum
from typing import Callable

from execution.execution_contract import ExecutionResult, ExecutionStatus, OrderIntent


class ExecutionLifecycleAction(str, Enum):
    EXECUTE = "EXECUTE"
    DO_NOT_RETRY = "DO_NOT_RETRY"
    RECONCILE = "RECONCILE"
    RETRY = "RETRY"


def classify_execution_result(result: ExecutionResult) -> ExecutionLifecycleAction:
    """Classify a canonical execution result without inferring broker state."""
    if result.status is ExecutionStatus.EXECUTED:
        return ExecutionLifecycleAction.EXECUTE
    if result.status in {ExecutionStatus.REJECTED, ExecutionStatus.FAILED}:
        return ExecutionLifecycleAction.DO_NOT_RETRY
    if result.status is ExecutionStatus.UNKNOWN:
        return ExecutionLifecycleAction.RECONCILE
    if result.status is ExecutionStatus.SUBMITTED:
        return ExecutionLifecycleAction.RECONCILE
    return ExecutionLifecycleAction.DO_NOT_RETRY
