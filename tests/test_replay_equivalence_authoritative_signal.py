from types import SimpleNamespace

from simulation.replay_equivalence import compare_replay_outputs


def _decision(*, signal="BUY CALL", authoritative_signal=None, include_authoritative=True):
    values = {"signal": signal, "valid": True}
    if include_authoritative:
        values["authoritative_signal"] = authoritative_signal
    return SimpleNamespace(**values)


def _intelligence():
    return SimpleNamespace(recommendation="BUY CALL", direction="BULLISH")


def test_legacy_snapshot_without_authoritative_signal_remains_equivalent():
    expected = _decision(include_authoritative=False)
    actual = _decision(authoritative_signal="BUY CALL")

    result = compare_replay_outputs(
        expected,
        actual,
        _intelligence(),
        _intelligence(),
    )

    assert result.equivalent is True
    assert result.mismatches == ()


def test_authoritative_signal_is_compared_when_recorded():
    expected = _decision(authoritative_signal="BUY PUT")
    actual = _decision(authoritative_signal="BUY CALL")

    result = compare_replay_outputs(
        expected,
        actual,
        _intelligence(),
        _intelligence(),
    )

    assert result.equivalent is False
    assert result.mismatches == ("decision.authoritative_signal",)


def test_legacy_snapshot_still_detects_other_decision_drift():
    expected = _decision(signal="BUY PUT", include_authoritative=False)
    actual = _decision(authoritative_signal="BUY CALL")

    result = compare_replay_outputs(
        expected,
        actual,
        _intelligence(),
        _intelligence(),
    )

    assert result.equivalent is False
    assert result.mismatches == ("decision.signal",)
