from execution.execution_contract import ExecutionAction, ExecutionResult, ExecutionStatus, OrderIntent
from execution.partial_fill_policy import evaluate_partial_fill


def intent(quantity=75):
    return OrderIntent(
        symbol="NIFTY",
        option_type="CE",
        strike=24000,
        action=ExecutionAction.BUY,
        quantity=quantity,
        limit_price=100,
        client_order_id="client-1",
    )


def result(filled, quantity=75, status=ExecutionStatus.EXECUTED):
    return ExecutionResult(status=status, intent=intent(quantity), filled_quantity=filled)


def test_full_fill_is_complete():
    decision = evaluate_partial_fill(result(75))
    assert decision.complete is True
    assert decision.follow_up_required is False


def test_partial_fill_requires_explicit_follow_up():
    decision = evaluate_partial_fill(result(25))
    assert decision.complete is False
    assert decision.follow_up_required is True


def test_zero_fill_on_executed_result_requires_reconciliation():
    decision = evaluate_partial_fill(result(0))
    assert decision.complete is False
    assert decision.follow_up_required is True


def test_overfill_is_not_accepted():
    decision = evaluate_partial_fill(result(100))
    assert decision.complete is False
    assert decision.follow_up_required is True


def test_negative_fill_is_not_accepted():
    decision = evaluate_partial_fill(result(-1))
    assert decision.complete is False
    assert decision.follow_up_required is True


def test_non_executed_status_is_not_treated_as_partial_fill():
    decision = evaluate_partial_fill(result(25, status=ExecutionStatus.UNKNOWN))
    assert decision.complete is False
    assert decision.follow_up_required is False
