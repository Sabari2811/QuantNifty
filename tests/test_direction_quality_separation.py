def apply_directional_quality(direction, quality_score):
    """
    Characterization helper for the intended R2-003 contract.

    Direction comes from SignalEngine.
    Quality comes from the institutional ScoreEngine.

    Quality must never manufacture or reverse direction.
    """
    if direction == "BUY CALL":
        return {
            "direction": "BUY CALL",
            "quality_score": quality_score,
            "signed_score": quality_score,
        }

    if direction == "BUY PUT":
        return {
            "direction": "BUY PUT",
            "quality_score": quality_score,
            "signed_score": -quality_score,
        }

    return {
        "direction": "WAIT",
        "quality_score": quality_score,
        "signed_score": 0,
    }


def test_buy_call_preserves_direction():
    result = apply_directional_quality("BUY CALL", 69)

    assert result["direction"] == "BUY CALL"
    assert result["quality_score"] == 69
    assert result["signed_score"] == 69


def test_buy_put_preserves_direction():
    result = apply_directional_quality("BUY PUT", 69)

    assert result["direction"] == "BUY PUT"
    assert result["quality_score"] == 69
    assert result["signed_score"] == -69


def test_wait_does_not_create_direction():
    result = apply_directional_quality("WAIT", 13)

    assert result["direction"] == "WAIT"
    assert result["quality_score"] == 13
    assert result["signed_score"] == 0