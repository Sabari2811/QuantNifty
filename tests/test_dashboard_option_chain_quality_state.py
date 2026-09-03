from core.data_provenance import AcquisitionProvenance, RuntimeDataProvenance
from dashboard.provenance_adapter import adapt_provenance


def test_option_chain_ui_state_is_unavailable_without_canonical_provenance():
    payload = adapt_provenance(RuntimeDataProvenance())

    assert payload["option_chain"] is None
    assert payload["option_chain_quality"] == "UNAVAILABLE"


def test_option_chain_ui_state_is_degraded_for_partial_coverage():
    option_chain = AcquisitionProvenance(
        source="options",
        expected_count=22,
        received_count=21,
        missing_count=1,
        integrity_status="VALID",
    )

    payload = adapt_provenance(RuntimeDataProvenance(option_chain=option_chain))

    assert payload["option_chain"]["coverage_status"] == "PARTIAL"
    assert payload["option_chain"]["integrity_status"] == "VALID"
    assert payload["option_chain_quality"] == "DEGRADED"


def test_option_chain_ui_state_is_degraded_for_invalid_integrity():
    option_chain = AcquisitionProvenance(
        source="options",
        expected_count=22,
        received_count=22,
        missing_count=0,
        integrity_status="INVALID",
    )

    payload = adapt_provenance(RuntimeDataProvenance(option_chain=option_chain))

    assert payload["option_chain"]["coverage_status"] == "COMPLETE"
    assert payload["option_chain"]["integrity_status"] == "INVALID"
    assert payload["option_chain_quality"] == "DEGRADED"


def test_option_chain_ui_state_is_ready_only_when_complete_and_not_invalid_or_suspect():
    option_chain = AcquisitionProvenance(
        source="options",
        expected_count=22,
        received_count=22,
        missing_count=0,
        integrity_status="VALID",
    )

    payload = adapt_provenance(RuntimeDataProvenance(option_chain=option_chain))

    assert payload["option_chain_quality"] == "READY"
