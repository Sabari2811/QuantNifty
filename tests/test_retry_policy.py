from execution.execution_contract import ExecutionAction, ExecutionResult, ExecutionStatus, OrderIntent
from execution.retry_policy import evaluate_retry


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


def result(status):
    return ExecutionResult(status=status, intent=intent())


def test_unknown_requires_reconciliation_before_retry():
    decision = evaluate_retry(result(ExecutionStatus.UNKNOWN), retry_count=0, max_retries=3)
    assert decision.allowed is False
    assert decision.reason == "Execution outcome requires reconciliation before retry."


def test_submitted_requires_reconciliation_before_retry():
    decision = evaluate_retry(result(ExecutionStatus.SUBMITTED), retry_count=0, max_retries=3)
    assert decision.allowed is False
    assert decision.reason == "Execution outcome requires reconciliation before retry."


def test_rejected_is_never_automatically_retried():
    decision = evaluate_retry(result(ExecutionStatus.REJECTED), retry_count=0, max_retries=3)
    assert decision.allowed is False


def test_failed_can_retry_only_within_explicit_limit():
    decision = evaluate_retry(result(ExecutionStatus.FAILED), retry_count=0, max_retries=1)
    assert decision.allowed is True


def test_failed_at_limit_is_not_retried():
    decision = evaluate_retry(result(ExecutionStatus.FAILED), retry_count=1, max_retries=1)
    assert decision.allowed is False


def test_invalid_retry_counts_are_rejected():
    try:
        evaluate_retry(result(ExecutionStatus.FAILED), retry_count=-1)
    except ValueError:
        pass
    else:
        raise AssertionError("negative retry_count must raise ValueError")
