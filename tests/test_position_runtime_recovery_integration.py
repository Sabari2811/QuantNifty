from datetime import datetime

from execution.position_recovery import evaluate_position_recovery
from execution.position_recovery_runtime import recover_open_positions
from execution.position_state import PositionState, PositionStatus
from execution.position_state_store import SQLitePositionStateStore


def _position(client_order_id="client-1", status=PositionStatus.OPEN):
    return PositionState(
        client_order_id=client_order_id,
        broker_order_id=f"broker-{client_order_id}",
        symbol="NIFTY",
        option_type="CE",
        strike=24300,
        quantity=50,
        entry_price=100.0,
        current_price=110.0,
        stop_loss=90.0,
        target=120.0,
        status=status,
        opened_at=datetime(2026, 9, 5, 9, 15),
        closed_at=(datetime(2026, 9, 5, 10, 0) if status is PositionStatus.CLOSED else None),
    )


def test_persisted_open_position_requires_reconciliation(tmp_path):
    with SQLitePositionStateStore(str(tmp_path / "positions.db")) as store:
        position = _position()
        store.save(position)
        recovered = recover_open_positions(store)
        decision = evaluate_position_recovery(recovered.positions[0])

    assert recovered.safe_to_continue is True
    assert decision.safe_to_continue is False
    assert decision.requires_reconciliation is True


def test_persisted_closed_position_is_terminal(tmp_path):
    with SQLitePositionStateStore(str(tmp_path / "positions.db")) as store:
        position = _position(status=PositionStatus.CLOSED)
        store.save(position)
        recovered = recover_open_positions(store)

    assert recovered.positions == ()
    decision = evaluate_position_recovery(position)
    assert decision.safe_to_continue is True
    assert decision.requires_reconciliation is False
