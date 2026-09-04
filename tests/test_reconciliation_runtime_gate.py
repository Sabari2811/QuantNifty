from execution.execution_contract import ExecutionAction, ExecutionResult, ExecutionStatus, OrderIntent
from execution.reconciliation import ReconciliationReport, ReconciliationStatus
from execution.reconciliation_runtime_gate import evaluate_runtime_reconciliation


def make_result(status):
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


def report(status):
    return ReconciliationReport(status=status, local_count=1, broker_count=1)


def test_executed_needs_no_runtime_reconciliation():
    decision = evaluate_runtime_reconciliation(make_result(ExecutionStatus.EXECUTED), None)
    assert decision.safe_to_continue is True
    assert decision.requires_manual_resolution is False


def test_unknown_without_report_blocks():
    decision = evaluate_runtime_reconciliation(make_result(ExecutionStatus.UNKNOWN), None)
    assert decision.safe_to_continue is False
    assert decision.requires_manual_resolution is False


def test_submitted_without_report_blocks():
    decision = evaluate_runtime_reconciliation(make_result(ExecutionStatus.SUBMITTED), None)
    assert decision.safe_to_continue is False


def test_matching_report_allows_continuation():
    decision = evaluate_runtime_reconciliation(
        make_result(ExecutionStatus.UNKNOWN), report(ReconciliationStatus.MATCH)
    )
    assert decision.safe_to_continue is True
    assert decision.requires_manual_resolution is False


def test_mismatch_requires_manual_resolution():
    decision = evaluate_runtime_reconciliation(
        make_result(ExecutionStatus.UNKNOWN), report(ReconciliationStatus.MISMATCH)
    )
    assert decision.safe_to_continue is False
    assert decision.requires_manual_resolution is True


def test_unknown_report_remains_blocked():
    decision = evaluate_runtime_reconciliation(
        make_result(ExecutionStatus.SUBMITTED), report(ReconciliationStatus.UNKNOWN)
    )
    assert decision.safe_to_continue is False
    assert decision.requires_manual_resolution is False


def test_missing_execution_result_blocks():
    decision = evaluate_runtime_reconciliation(None, report(ReconciliationStatus.MATCH))
    assert decision.safe_to_continue is False
