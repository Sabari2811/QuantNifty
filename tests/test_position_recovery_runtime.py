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
        closed_at=None,
    )


def test_recovery_loads_persisted_open_positions(tmp_path):
    with SQLitePositionStateStore(str(tmp_path / "positions.db")) as store:
        position = _position()
        store.save(position)
        decision = recover_open_positions(store)

    assert decision.safe_to_continue is True
    assert decision.positions == (position,)


def test_recovery_excludes_closed_positions(tmp_path):
    with SQLitePositionStateStore(str(tmp_path / "positions.db")) as store:
        store.save(_position("client-1"))
        store.save(
            _position(
                "client-2",
                PositionStatus.CLOSED,
            ).__class__(
                **{
                    **_position("client-2", PositionStatus.CLOSED).__dict__,
                    "closed_at": __import__("datetime").datetime.now(),
                }
            )
        )
        decision = recover_open_positions(store)

    assert decision.positions == (_position("client-1"),)


def test_recovery_without_store_fails_closed():
    decision = recover_open_positions(None)
    assert decision.safe_to_continue is False
    assert decision.positions == ()
