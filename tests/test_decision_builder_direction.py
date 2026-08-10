from decision.constants import Signal
from decision.decision_builder import DecisionBuilder


class Market:
    def __init__(self):
        self.dealer = "LONG"
        self.institutional = {"score": 69}
        self.probability = 88


def build_decision(score, direction=None):
    return DecisionBuilder().build(
        market=Market(),
        score=score,
        breakdown={"final": score},
        reasons=[],
        direction=direction,
    )


def test_authoritative_buy_call_direction_is_preserved():
    decision = build_decision(
        score=-69,
        direction=Signal.BUY_CALL.value,
    )

    assert decision.signal.name == Signal.BUY_CALL.value


def test_authoritative_buy_put_direction_is_preserved():
    decision = build_decision(
        score=69,
        direction=Signal.BUY_PUT.value,
    )

    assert decision.signal.name == Signal.BUY_PUT.value


def test_authoritative_wait_direction_is_preserved():
    decision = build_decision(
        score=69,
        direction=Signal.WAIT.value,
    )

    assert decision.signal.name == Signal.WAIT.value


def test_authoritative_direction_can_use_positive_call_score():
    decision = build_decision(
        score=69,
        direction=Signal.BUY_CALL.value,
    )

    assert decision.signal.name == Signal.BUY_CALL.value
    assert decision.signal.confidence == 69


def test_authoritative_direction_can_use_negative_put_score():
    decision = build_decision(
        score=-69,
        direction=Signal.BUY_PUT.value,
    )

    assert decision.signal.name == Signal.BUY_PUT.value
    assert decision.signal.confidence == 69


def test_invalid_authoritative_direction_is_rejected():
    try:
        build_decision(
            score=69,
            direction="INVALID",
        )
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_legacy_score_behavior_remains_available_without_direction():
    call_decision = build_decision(score=80)

    assert call_decision.signal.name == Signal.BUY_CALL.value

    put_decision = build_decision(score=-80)

    assert put_decision.signal.name == Signal.BUY_PUT.value

    wait_decision = build_decision(score=0)

    assert wait_decision.signal.name == Signal.WAIT.value