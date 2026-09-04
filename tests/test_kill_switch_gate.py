from execution.execution_contract import ExecutionAction, ExecutionStatus, OrderIntent
from execution.kill_switch import KillSwitch
from execution.kill_switch_gate import evaluate_kill_switch_gate, rejected_result


def make_intent():
    return OrderIntent(
        symbol="NIFTY",
        option_type="CE",
        strike=24000,
        action=ExecutionAction.BUY,
        quantity=75,
        limit_price=100,
        client_order_id="client-1",
    )


def test_inactive_kill_switch_allows_intent():
    decision = evaluate_kill_switch_gate(KillSwitch(), make_intent())

    assert decision.allowed is True


def test_active_kill_switch_blocks_intent():
    switch = KillSwitch()
    switch.activate("Emergency stop")

    decision = evaluate_kill_switch_gate(switch, make_intent())

    assert decision.allowed is False
    assert decision.reason == "Kill switch active: Emergency stop"


def test_missing_kill_switch_state_fails_closed():
    decision = evaluate_kill_switch_gate(None, make_intent())

    assert decision.allowed is False
    assert "state is unavailable" in decision.reason


def test_no_intent_does_not_create_execution_block():
    decision = evaluate_kill_switch_gate(KillSwitch(enabled=True, reason="halt"), None)

    assert decision.allowed is True


def test_kill_switch_rejection_maps_to_canonical_result():
    switch = KillSwitch()
    switch.activate("Emergency stop")
    decision = evaluate_kill_switch_gate(switch, make_intent())

    result = rejected_result(make_intent(), decision)

    assert result.status is ExecutionStatus.REJECTED
    assert result.reason == "Kill switch active: Emergency stop"
