from datetime import datetime, timezone

from core.data_provenance import AcquisitionProvenance, RuntimeDataProvenance
from dashboard.provenance_adapter import adapt_provenance


def test_provenance_adapter_preserves_independent_quality_states():
    acquired = datetime(2026, 8, 26, tzinfo=timezone.utc)
    provenance = RuntimeDataProvenance(
        spot=AcquisitionProvenance(
            source="INDMoney index quote",
            acquired_at=acquired,
            expected_count=1,
            received_count=1,
            missing_count=0,
            freshness_verified=False,
        ),
        option_chain=AcquisitionProvenance(
            source="INDMoney option quotes",
            acquired_at=acquired,
            expected_count=22,
            received_count=22,
            missing_count=0,
            freshness_verified=False,
            integrity_status="SUSPECT",
            integrity_reasons=("pe_ltp_below_intrinsic",),
        ),
    )

    payload = adapt_provenance(provenance)

    assert payload["spot"]["coverage_status"] == "COMPLETE"
    assert payload["spot"]["integrity_status"] == "UNVERIFIED"
    assert payload["spot"]["freshness_status"] == "UNVERIFIED"

    assert payload["option_chain"]["coverage_status"] == "COMPLETE"
    assert payload["option_chain"]["integrity_status"] == "SUSPECT"
    assert payload["option_chain"]["freshness_status"] == "UNVERIFIED"
    assert payload["option_chain"]["integrity_reasons"] == ("pe_ltp_below_intrinsic",)


def test_provenance_adapter_preserves_partial_coverage():
    provenance = RuntimeDataProvenance(
        option_chain=AcquisitionProvenance(
            source="INDMoney option quotes",
            expected_count=22,
            received_count=20,
            missing_count=2,
            freshness_verified=False,
        )
    )

    payload = adapt_provenance(provenance)

    assert payload["option_chain"]["coverage_ratio"] == 90.0
    assert payload["option_chain"]["coverage_status"] == "PARTIAL"
    assert payload["option_chain"]["missing_count"] == 2
