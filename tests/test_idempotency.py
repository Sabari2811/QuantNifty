from execution.idempotency import IdempotencyStatus, OrderIdempotencyGuard


def test_first_client_order_id_is_new_and_reserved():
    guard = OrderIdempotencyGuard()

    result = guard.check_and_reserve("client-1")

    assert result.status is IdempotencyStatus.NEW
    assert result.client_order_id == "client-1"
    assert guard.contains("client-1") is True


def test_repeated_client_order_id_is_duplicate():
    guard = OrderIdempotencyGuard()
    guard.check_and_reserve("client-1")

    result = guard.check_and_reserve("client-1")

    assert result.status is IdempotencyStatus.DUPLICATE
    assert result.reason == "Client order already reserved"


def test_empty_client_order_id_is_invalid_and_not_reserved():
    guard = OrderIdempotencyGuard()

    result = guard.check_and_reserve("   ")

    assert result.status is IdempotencyStatus.INVALID
    assert result.client_order_id == ""
    assert guard.contains("") is False


def test_distinct_client_order_ids_are_independently_reservable():
    guard = OrderIdempotencyGuard()

    first = guard.check_and_reserve("client-1")
    second = guard.check_and_reserve("client-2")

    assert first.status is IdempotencyStatus.NEW
    assert second.status is IdempotencyStatus.NEW
