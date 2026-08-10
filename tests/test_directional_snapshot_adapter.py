from decision.scoring.directional_score_adapter import DirectionalScoreAdapter


def adapt_snapshot(snapshot):
    """
    R2-003-C characterization helper.

    Reads the canonical signal and institutional score
    already produced by the analytics layer.
    """
    signal = snapshot["signal"]
    institutional = snapshot["institutional_score"]

    direction = signal.get("signal", "WAIT")
    quality = institutional.get("score", 0)

    return DirectionalScoreAdapter().adapt(
        direction,
        quality,
    )


def test_snapshot_buy_call_preserves_direction_and_quality():
    snapshot = {
        "signal": {
            "signal": "BUY CALL",
        },
        "institutional_score": {
            "score": 69,
        },
    }

    result = adapt_snapshot(snapshot)

    assert result["direction"] == "BUY CALL"
    assert result["quality_score"] == 69
    assert result["signed_score"] == 69


def test_snapshot_buy_put_preserves_direction_and_quality():
    snapshot = {
        "signal": {
            "signal": "BUY PUT",
        },
        "institutional_score": {
            "score": 69,
        },
    }

    result = adapt_snapshot(snapshot)

    assert result["direction"] == "BUY PUT"
    assert result["quality_score"] == 69
    assert result["signed_score"] == -69


def test_snapshot_wait_does_not_create_direction():
    snapshot = {
        "signal": {
            "signal": "WAIT",
        },
        "institutional_score": {
            "score": 13,
        },
    }

    result = adapt_snapshot(snapshot)

    assert result["direction"] == "WAIT"
    assert result["quality_score"] == 13
    assert result["signed_score"] == 0