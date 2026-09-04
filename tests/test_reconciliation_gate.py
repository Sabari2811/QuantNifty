from execution.execution_contract import ExecutionAction, ExecutionResult, ExecutionStatus, OrderIntent
from execution.reconciliation import ReconciliationReport, ReconciliationStatus
from execution.reconciliation_gate import evaluate_reconciliation_gate


def _result(status: ExecutionStatus) -> ExecutionResult:
    intent = OrderIntent(
        symbol="NIFTY",
        option_type="CE",
        strike=24000,
        action=ExecutionAction.BUY,
        quantity=75,
        limit_price=100,
        client_order_id="client-1",
    )
    return ExecutionResult(status=status, intent=intent)


def _report(status: ReconciliationStatus) -> ReconciliationReport:
    return ReconciliationReport(status=status, local_count=1, broker_count=1)


def test_unknown_without_report_is_blocked():
    decision = evaluate_reconciliation_gate(_result(ExecutionStatus.UNKNOWN), None)
    assert decision.allowed is False
    assert decision.reason == "Execution outcome is ambiguous; reconciliation report is required."


def test_submitted_without_report_is_blocked():
    decision = evaluate_reconciliation_gate(_result(ExecutionStatus.SUBMITTED), None)
    assert decision.allowed is False


def test_unknown_with_match_is_allowed_to_continue():
    decision = evaluate_reconciliation_gate(_result(ExecutionStatus.UNKNOWN), _report(ReconciliationStatus.MATCH))
    assert decision.allowed is True


def test_submitted_with_match_is_allowed_to_continue():
    decision = evaluate_reconciliation_gate(_result(ExecutionStatus.SUBMITTED), _report(ReconciliationStatus.MATCH))
    assert decision.allowed is True


def test_mismatch_blocks_retry():
    decision = evaluate_reconciliation_gate(_result(ExecutionStatus.UNKNOWN), _report(ReconciliationStatus.MISMATCH))
    assert decision.allowed is False
    assert "manual resolution" in decision.reason


def test_unknown_reconciliation_state_blocks_retry():
    decision = evaluate_reconciliation_gate(_result(ExecutionStatus.UNKNOWN), _report(ReconciliationStatus.UNKNOWN))
    assert decision.allowed is False


def test_terminal_result_does_not_require_reconciliation():
    decision = evaluate_reconciliation_gate(_result(ExecutionStatus.FAILED), None)
    assert decision.allowed is True
