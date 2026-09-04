from execution.execution_contract import ExecutionAction, ExecutionResult, ExecutionStatus, OrderIntent
from execution.execution_lifecycle import ExecutionLifecycleAction, classify_execution_result


def intent():
    return OrderIntent(
        symbol="NIFTY",
        option_type="CE",
        strike=24000,
        action=ExecutionAction.BUY,
        quantity=75,
        limit_price=100,
        client_order_id="client-1",
    )


def test_executed_is_terminal_success():
    result = ExecutionResult(ExecutionStatus.EXECUTED, intent(), filled_quantity=75, average_fill_price=100)
    assert classify_execution_result(result) is ExecutionLifecycleAction.EXECUTE


def test_rejected_is_not_retried():
    result = ExecutionResult(ExecutionStatus.REJECTED, intent(), reason="Rejected")
    assert classify_execution_result(result) is ExecutionLifecycleAction.DO_NOT_RETRY


def test_failed_is_not_retried_without_explicit_retry_policy():
    result = ExecutionResult(ExecutionStatus.FAILED, intent(), reason="Transport failure")
    assert classify_execution_result(result) is ExecutionLifecycleAction.DO_NOT_RETRY


def test_unknown_requires_reconciliation():
    result = ExecutionResult(ExecutionStatus.UNKNOWN, intent(), reason="Timeout")
    assert classify_execution_result(result) is ExecutionLifecycleAction.RECONCILE


def test_submitted_requires_reconciliation_before_any_retry():
    result = ExecutionResult(ExecutionStatus.SUBMITTED, intent())
    assert classify_execution_result(result) is ExecutionLifecycleAction.RECONCILE


def test_not_submitted_does_not_create_implicit_retry():
    result = ExecutionResult(ExecutionStatus.NOT_SUBMITTED, intent())
    assert classify_execution_result(result) is ExecutionLifecycleAction.DO_NOT_RETRY
