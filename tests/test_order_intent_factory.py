from decision.models.decision import Decision
from decision.models.execution_plan import ExecutionPlan
from decision.models.option_contract import OptionContract
from execution.order_intent_factory import build_order_intent


def executable_decision(signal="BUY CALL", client_price=100, expiry="2026-09-10"):
    decision = Decision()
    decision.valid = True
    decision.signal.name = signal
    decision.strategy_name = "TEST"
    decision.trade.option_type = "CE" if signal == "BUY CALL" else "PE"
    decision.trade.strike = 24000
    decision.trade.entry = client_price
    decision.trade.contract = OptionContract(
        strike=24000,
        option_type=decision.trade.option_type,
        expiry=expiry,
    )
    decision.trade.execution = ExecutionPlan(lot_size=75, lots=1)
    return decision


def test_factory_builds_canonical_buy_intent():
    intent = build_order_intent(executable_decision())

    assert intent is not None
    assert intent.symbol == "NIFTY"
    assert intent.option_type == "CE"
    assert intent.strike == 24000
    assert intent.quantity == 75
    assert intent.limit_price == 100
    assert intent.metadata["expiry"] == "2026-09-10"
    assert intent.client_order_id.startswith("qn-")


def test_factory_is_deterministic_for_same_execution_identity():
    first = build_order_intent(executable_decision())
    second = build_order_intent(executable_decision())

    assert first.client_order_id == second.client_order_id


def test_factory_distinguishes_changed_execution_identity():
    first = build_order_intent(executable_decision(client_price=100))
    second = build_order_intent(executable_decision(client_price=101))

    assert first.client_order_id != second.client_order_id


def test_factory_distinguishes_changed_expiry():
    first = build_order_intent(executable_decision(expiry="2026-09-10"))
    second = build_order_intent(executable_decision(expiry="2026-09-17"))

    assert first.client_order_id != second.client_order_id


def test_factory_does_not_create_intent_for_wait_or_invalid():
    assert build_order_intent(executable_decision(signal="WAIT")) is None

    invalid = executable_decision()
    invalid.valid = False
    assert build_order_intent(invalid) is None
