from datetime import datetime, timezone

from analytics.intelligence.result import DataQuality
from application.intelligence_service import IntelligenceService
from core.data_provenance import (
    AcquisitionProvenance,
    RuntimeDataProvenance,
)


def test_acquisition_provenance_is_immutable_and_tracks_completeness():
    provenance = AcquisitionProvenance(
        source="test",
        acquired_at=datetime.now(timezone.utc),
        expected_count=4,
        received_count=3,
        missing_count=1,
    )

    assert provenance.complete is False

    try:
        provenance.received_count = 4
    except AttributeError:
        pass
    else:
        raise AssertionError("AcquisitionProvenance must be immutable")


def test_runtime_provenance_complete_when_all_required_inputs_are_complete():
    complete = AcquisitionProvenance(
        source="test",
        expected_count=1,
        received_count=1,
        missing_count=0,
    )

    runtime = RuntimeDataProvenance(
        spot=complete,
        option_chain=complete,
        candles=complete,
    )

    assert runtime.complete is True


def test_provider_timestamp_round_trips_without_loss():
    provider_timestamp = datetime(2026, 8, 24, 10, 5, tzinfo=timezone.utc)
    original = AcquisitionProvenance(
        source="historical",
        acquired_at=datetime(2026, 8, 24, 10, 6, tzinfo=timezone.utc),
        provider_timestamp=provider_timestamp,
        expected_count=1,
        received_count=1,
        missing_count=0,
        freshness_verified=True,
        freshness_seconds=60.0,
        reasons=("provider_candle_timestamp",),
    )

    restored = AcquisitionProvenance.from_dict({
        "source": original.source,
        "acquired_at": original.acquired_at.isoformat(),
        "provider_timestamp": original.provider_timestamp.isoformat(),
        "expected_count": original.expected_count,
        "received_count": original.received_count,
        "missing_count": original.missing_count,
        "freshness_verified": original.freshness_verified,
        "freshness_seconds": original.freshness_seconds,
        "reasons": list(original.reasons),
    })

    assert restored == original


def test_provider_timestamp_field_is_append_only_for_positional_compatibility():
    acquired_at = datetime(2026, 8, 24, 10, 6, tzinfo=timezone.utc)
    provenance = AcquisitionProvenance(
        "historical",
        acquired_at,
        1,
        1,
        0,
        True,
        60.0,
        ("provider_candle_timestamp",),
    )

    assert provenance.expected_count == 1
    assert provenance.received_count == 1
    assert provenance.provider_timestamp is None


def test_integrity_fields_round_trip_without_changing_freshness():
    original = AcquisitionProvenance(
        source="options",
        expected_count=2,
        received_count=2,
        missing_count=0,
        freshness_verified=False,
        reasons=("provider_quote_timestamp_unavailable",),
        integrity_status="SUSPECT",
        integrity_reasons=("ce_ltp_below_intrinsic",),
    )

    restored = AcquisitionProvenance.from_dict({
        "source": original.source,
        "acquired_at": original.acquired_at.isoformat(),
        "expected_count": original.expected_count,
        "received_count": original.received_count,
        "missing_count": original.missing_count,
        "freshness_verified": original.freshness_verified,
        "reasons": list(original.reasons),
        "integrity_status": original.integrity_status,
        "integrity_reasons": list(original.integrity_reasons),
    })

    assert restored == original
    assert restored.freshness_verified is False
    assert restored.integrity_status == "SUSPECT"


def test_data_quality_is_derived_from_runtime_provenance():
    class Context:
        data_provenance = RuntimeDataProvenance(
            spot=AcquisitionProvenance(
                source="spot",
                expected_count=1,
                received_count=1,
                missing_count=0,
            ),
            option_chain=AcquisitionProvenance(
                source="options",
                expected_count=10,
                received_count=8,
                missing_count=2,
            ),
        )

    quality = IntelligenceService._build_data_quality(Context())

    assert isinstance(quality, DataQuality)
    assert quality.score == 80.0
    assert quality.incomplete is True
    assert quality.stale is False
    assert any(reason.startswith("incomplete:options") for reason in quality.reasons)
    assert any(reason.startswith("freshness_unverified:options") for reason in quality.reasons)


def test_data_quality_marks_invalid_integrity_separately_from_freshness():
    class Context:
        data_provenance = RuntimeDataProvenance(
            option_chain=AcquisitionProvenance(
                source="options",
                expected_count=2,
                received_count=2,
                missing_count=0,
                freshness_verified=False,
                integrity_status="INVALID",
                integrity_reasons=("negative_ce_ltp",),
            )
        )

    quality = IntelligenceService._build_data_quality(Context())

    assert quality.invalid is True
    assert quality.freshness_verified is False
    assert "integrity_invalid:options" in quality.reasons
    assert "negative_ce_ltp" in quality.reasons
