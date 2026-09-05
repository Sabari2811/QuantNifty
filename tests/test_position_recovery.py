from datetime import datetime

from execution.position_recovery import evaluate_position_recovery, recover_open_positions
from execution.position_state import PositionState, PositionStatus


def _position(status=PositionStatus.OPEN, **overrides):
    values = dict(
        client_order_id="client-1",
        broker_order_id="broker-1",
        symbol="NIFTY",
        option_type="CE",
        strike=24300,
        quantity=50,
        entry_price=100.0,
        current_price=110.0,
        stop_loss=90.0,
        target=120.0,
        trailing_stop=None,
        status=status,
        opened_at=datetime(2026, 9, 5, 9, 15),
        closed_at=None,
    )
    if status is PositionStatus.CLOSED:
        values["closed_at"] = datetime(2026, 9, 5, 10, 0)
    values.update(overrides)
    return PositionState(**values)


def test_open_position_requires_reconciliation():
    decision = evaluate_position_recovery(_position())
    assert decision.safe_to_continue is False
    assert decision.requires_reconciliation is True
    assert decision.requires_manual_resolution is False


def test_closed_position_can_continue():
    decision = evaluate_position_recovery(_position(PositionStatus.CLOSED))
    assert decision.safe_to_continue is True
    assert decision.requires_reconciliation is False
    assert decision.requires_manual_resolution is False


def test_missing_position_does_not_infer_state():
    decision = evaluate_position_recovery(None)
    assert decision.safe_to_continue is False
    assert decision.requires_reconciliation is False


def test_unknown_position_blocks_for_manual_resolution():
    decision = evaluate_position_recovery(_position(PositionStatus.UNKNOWN))
    assert decision.safe_to_continue is False
    assert decision.requires_reconciliation is True
    assert decision.requires_manual_resolution is True


def test_recover_open_positions_delegates_to_persistent_store():
    class Store:
        def open_positions(self):
            return [_position(), _position(client_order_id="client-2")]

    assert recover_open_positions(Store()) == (
        _position(),
        _position(client_order_id="client-2"),
    )
