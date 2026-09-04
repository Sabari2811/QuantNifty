from __future__ import annotations

from types import SimpleNamespace

from execution.execution_contract import ExecutionAction
from execution.order_intent_factory import build_order_intent


def test_build_order_intent_can_be_attached_to_runtime_context():
    decision = SimpleNamespace(
        valid=True,
        signal=SimpleNamespace(name="BUY CALL"),
        strategy_name="TEST",
        trade=SimpleNamespace(
            symbol="NIFTY",
            option_type="CE",
            strike=24000,
            entry=100.0,
            execution=SimpleNamespace(lot_size=75, lots=1),
        ),
    )

    intent = build_order_intent(decision)

    assert intent is not None
    assert intent.action is ExecutionAction.BUY
    assert intent.quantity == 75
    assert intent.client_order_id.startswith("qn-")
