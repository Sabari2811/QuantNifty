from decision.scoring.directional_score_adapter import DirectionalScoreAdapter


def test_buy_call_creates_positive_signed_score():
    result = DirectionalScoreAdapter().adapt("BUY CALL", 69)

    assert result["direction"] == "BUY CALL"
    assert result["quality_score"] == 69
    assert result["signed_score"] == 69


def test_buy_put_creates_negative_signed_score():
    result = DirectionalScoreAdapter().adapt("BUY PUT", 69)

    assert result["direction"] == "BUY PUT"
    assert result["quality_score"] == 69
    assert result["signed_score"] == -69


def test_wait_creates_zero_signed_score():
    result = DirectionalScoreAdapter().adapt("WAIT", 13)

    assert result["direction"] == "WAIT"
    assert result["quality_score"] == 13
    assert result["signed_score"] == 0


def test_negative_quality_is_clamped_to_zero():
    result = DirectionalScoreAdapter().adapt("BUY CALL", -10)

    assert result["quality_score"] == 0
    assert result["signed_score"] == 0


def test_unknown_direction_is_rejected():
    try:
        DirectionalScoreAdapter().adapt("UNKNOWN", 69)
        assert False, "Expected ValueError"
    except ValueError:
        pass