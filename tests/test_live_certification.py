import pytest

from monitoring.live_certification import certify_live_session


def _record(**overrides):
    record = {
        "evidence_state": "VALID_LIVE",
        "provider": "INDMONEY",
        "provider_mode": "LIVE_PROVIDER",
        "spot": 25123.4,
        "option_chain_coverage": "COMPLETE",
        "option_chain_integrity": "VALID",
        "provenance_freshness": "FRESH",
        "persistence_status": "DURABLE_DATABASE",
    }
    record.update(overrides)
    return record


def test_certification_requires_multiple_valid_live_cycles():
    result = certify_live_session([_record(), _record(), _record()])
    assert result.passed is True
    assert result.cycles_checked == 3
    assert result.valid_live_cycles == 3
    assert result.reasons == ()


def test_certification_fails_closed_on_stale_cycle():
    result = certify_live_session([
        _record(),
        _record(provenance_freshness="NOT_FRESH"),
        _record(),
    ])
    assert result.passed is False
    assert result.valid_live_cycles == 2
    assert "cycle_2:provenance_not_fresh" in result.reasons


def test_certification_fails_when_persistence_is_partial():
    result = certify_live_session([_record(), _record(), _record(persistence_status="LOCAL_OR_PARTIAL")])
    assert result.passed is False
    assert "cycle_3:persistence_not_durable" in result.reasons


def test_certification_requires_minimum_cycle_count():
    result = certify_live_session([_record(), _record()], min_cycles=3)
    assert result.passed is False
    assert "insufficient_cycles:2<3" in result.reasons


def test_certification_rejects_non_numeric_spot():
    result = certify_live_session([_record(spot=None), _record(), _record()])
    assert result.passed is False
    assert "cycle_1:spot_missing_or_invalid" in result.reasons


def test_invalid_minimum_is_rejected():
    with pytest.raises(ValueError):
        certify_live_session([], min_cycles=0)
