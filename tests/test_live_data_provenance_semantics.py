from datetime import datetime, timezone

from core.data_provenance import AcquisitionProvenance, RuntimeDataProvenance


def test_acquisition_provenance_exposes_separate_coverage_freshness_and_integrity():
    provenance = AcquisitionProvenance(
        source="INDMoney option quotes",
        expected_count=22,
        received_count=20,
        missing_count=2,
        freshness_verified=False,
        integrity_status="SUSPECT",
        integrity_reasons=("ce_ltp_below_intrinsic",),
    )

    assert provenance.coverage_ratio == 20 / 22 * 100
    assert provenance.coverage_status == "PARTIAL"
    assert provenance.freshness_status == "UNVERIFIED"
    assert provenance.integrity_status == "SUSPECT"
    assert provenance.status == "SUSPECT"


def test_complete_valid_fresh_provenance_is_valid():
    provenance = AcquisitionProvenance(
        source="INDMoney historical candles:NIDX_40000001",
        acquired_at=datetime.now(timezone.utc),
        provider_timestamp=datetime.now(timezone.utc),
        expected_count=1,
        received_count=1,
        missing_count=0,
        freshness_verified=True,
        freshness_seconds=12.0,
        integrity_status="VALID",
    )

    assert provenance.coverage_ratio == 100.0
    assert provenance.coverage_status == "COMPLETE"
    assert provenance.freshness_status == "VERIFIED"
    assert provenance.status == "VALID"


def test_runtime_provenance_aggregate_coverage_is_deterministic():
    runtime = RuntimeDataProvenance(
        spot=AcquisitionProvenance(
            source="spot",
            expected_count=1,
            received_count=1,
            missing_count=0,
        ),
        option_chain=AcquisitionProvenance(
            source="options",
            expected_count=22,
            received_count=20,
            missing_count=2,
        ),
        candles=AcquisitionProvenance(
            source="candles",
            expected_count=1,
            received_count=1,
            missing_count=0,
        ),
    )

    assert runtime.coverage_ratio == 22 / 24 * 100
    assert runtime.complete is False
    payload = runtime.as_dict()
    assert payload["option_chain"]["coverage_status"] == "PARTIAL"
    assert payload["option_chain"]["freshness_status"] == "UNVERIFIED"
