from execution.execution_contract import ExecutionAction, OrderIntent
from execution.execution_contract import ExecutionStatus, ExecutionResult
from execution.kill_switch import KillSwitch
from execution.reconciliation import ReconciliationReport, ReconciliationStatus
from execution.runtime_safety_gate import evaluate_runtime_safety


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


def report(status):
    return ReconciliationReport(status=status, local_count=1, broker_count=1)


def active_switch():
    switch = KillSwitch()
    switch.activate("Operator stop")
    return switch


def inactive_switch():
    return KillSwitch()


def test_active_kill_switch_blocks_runtime_execution():
    decision = evaluate_runtime_safety(intent=intent(), kill_switch=active_switch())
    assert decision.allowed is False
    assert "Kill switch active" in decision.reason


def test_missing_kill_switch_state_blocks_runtime_execution():
    decision = evaluate_runtime_safety(intent=intent(), kill_switch=None)
    assert decision.allowed is False
    assert "unavailable" in decision.reason.lower()


def test_reconciliation_required_blocks_without_match():
    decision = evaluate_runtime_safety(
        intent=intent(),
        kill_switch=inactive_switch(),
        reconciliation_result=result(ExecutionStatus.UNKNOWN),
        reconciliation_report=report(ReconciliationStatus.UNKNOWN),
    )
    assert decision.allowed is False
    assert "reconciliation" in decision.reason.lower()


def test_reconciliation_match_allows_execution():
    decision = evaluate_runtime_safety(
        intent=intent(),
        kill_switch=inactive_switch(),
        reconciliation_result=result(ExecutionStatus.SUBMITTED),
        reconciliation_report=report(ReconciliationStatus.MATCH),
    )
    assert decision.allowed is True


def test_reconciliation_mismatch_blocks_execution():
    decision = evaluate_runtime_safety(
        intent=intent(),
        kill_switch=inactive_switch(),
        reconciliation_result=result(ExecutionStatus.UNKNOWN),
        reconciliation_report=report(ReconciliationStatus.MISMATCH),
    )
    assert decision.allowed is False
    assert "mismatch" in decision.reason.lower()


def test_terminal_execution_does_not_require_reconciliation():
    decision = evaluate_runtime_safety(
        intent=intent(),
        kill_switch=inactive_switch(),
        reconciliation_result=result(ExecutionStatus.EXECUTED),
        reconciliation_report=None,
    )
    assert decision.allowed is True
