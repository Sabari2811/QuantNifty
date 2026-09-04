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


def test_active_kill_switch_blocks_runtime_execution():
    decision = evaluate_runtime_safety(intent=intent(), kill_switch=KillSwitch(active=True))
    assert decision.allowed is False
    assert "Kill switch active" in decision.reason


def test_missing_kill_switch_state_blocks_runtime_execution():
    decision = evaluate_runtime_safety(intent=intent(), kill_switch=None)
    assert decision.allowed is False
    assert "unavailable" in decision.reason.lower()


def test_reconciliation_required_blocks_without_match():
    report = ReconciliationReport(
        status=ReconciliationStatus.UNKNOWN,
        local_count=1,
        broker_count=0,
    )
    decision = evaluate_runtime_safety(
        intent=intent(),
        kill_switch=KillSwitch(active=False),
        reconciliation_report=report,
        reconciliation_required=True,
    )
    assert decision.allowed is False
    assert "reconciliation" in decision.reason.lower()


def test_reconciliation_match_allows_execution():
    report = ReconciliationReport(
        status=ReconciliationStatus.MATCH,
        local_count=1,
        broker_count=1,
    )
    decision = evaluate_runtime_safety(
        intent=intent(),
        kill_switch=KillSwitch(active=False),
        reconciliation_report=report,
        reconciliation_required=True,
    )
    assert decision.allowed is True


def test_reconciliation_is_not_required_for_normal_new_execution():
    decision = evaluate_runtime_safety(
        intent=intent(),
        kill_switch=KillSwitch(active=False),
        reconciliation_required=False,
    )
    assert decision.allowed is True
