from datetime import datetime, timezone

from core.data_provenance import AcquisitionProvenance, RuntimeDataProvenance
from dashboard.components.option_chain import _option_chain_provenance


def _provenance():
    return RuntimeDataProvenance(
        option_chain=AcquisitionProvenance(
            source="INDMoney option quotes",
            acquired_at=datetime(2026, 8, 26, 1, 7, tzinfo=timezone.utc),
            expected_count=22,
            received_count=22,
            missing_count=0,
            freshness_verified=False,
            integrity_status="SUSPECT",
            integrity_reasons=("pe_ltp_below_intrinsic",),
            reasons=("provider_quote_timestamp_unavailable",),
        )
    )


def test_option_chain_ui_preserves_independent_backend_states():
    state = _option_chain_provenance(_provenance())

    assert state["coverage_status"] == "COMPLETE"
    assert state["coverage_ratio"] == 100.0
    assert state["integrity_status"] == "SUSPECT"
    assert state["freshness_status"] == "UNVERIFIED"
    assert state["source"] == "INDMoney option quotes"
    assert state["integrity_reasons"] == ("pe_ltp_below_intrinsic",)
    assert state["reasons"] == ("provider_quote_timestamp_unavailable",)


def test_option_chain_ui_preserves_partial_coverage_without_overwriting_integrity():
    provenance = RuntimeDataProvenance(
        option_chain=AcquisitionProvenance(
            source="INDMoney option quotes",
            expected_count=22,
            received_count=20,
            missing_count=2,
            freshness_verified=False,
            integrity_status="VALID",
        )
    )

    state = _option_chain_provenance(provenance)

    assert state["coverage_status"] == "PARTIAL"
    assert state["coverage_ratio"] == (20 / 22) * 100.0
    assert state["integrity_status"] == "VALID"
    assert state["freshness_status"] == "UNVERIFIED"
    assert state["missing_count"] == 2
