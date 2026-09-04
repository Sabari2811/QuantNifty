from execution.reconciliation import (
    PositionSnapshot,
    ReconciliationStatus,
    reconcile_positions,
)


def position(**overrides):
    values = {
        "client_order_id": "client-1",
        "symbol": "NIFTY",
        "option_type": "CE",
        "strike": 24000,
        "quantity": 75,
        "status": "OPEN",
        "broker_order_id": "broker-1",
    }
    values.update(overrides)
    return PositionSnapshot(**values)


def test_matching_positions_are_safe_to_continue():
    report = reconcile_positions([position()], [position()])

    assert report.status is ReconciliationStatus.MATCH
    assert report.safe_to_continue is True
    assert report.issues == ()


def test_missing_broker_position_is_mismatch():
    report = reconcile_positions([position()], [])

    assert report.status is ReconciliationStatus.MISMATCH
    assert report.safe_to_continue is False
    assert report.issues[0].reason == "Missing broker position"


def test_untracked_broker_position_is_mismatch():
    report = reconcile_positions([], [position()])

    assert report.status is ReconciliationStatus.MISMATCH
    assert report.issues[0].reason == "Untracked broker position"


def test_quantity_mismatch_is_mismatch():
    report = reconcile_positions([position()], [position(quantity=150)])

    assert report.status is ReconciliationStatus.MISMATCH
    assert report.issues[0].reason == "Quantity mismatch"


def test_identity_and_execution_shape_mismatch_is_explicit():
    report = reconcile_positions(
        [position(option_type="PE")],
        [position(option_type="CE")],
    )

    assert report.status is ReconciliationStatus.MISMATCH
    assert report.issues[0].reason == "Option type mismatch"


def test_unavailable_snapshot_is_unknown_not_empty_match():
    report = reconcile_positions(None, [])

    assert report.status is ReconciliationStatus.UNKNOWN
    assert report.safe_to_continue is False
    assert report.issues[0].reason == "Position snapshot unavailable"


def test_generator_inputs_are_materialized_once():
    report = reconcile_positions((p for p in [position()]), (p for p in [position()]))

    assert report.status is ReconciliationStatus.MATCH
    assert report.local_count == 1
    assert report.broker_count == 1
