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
    assert any(
        reason.startswith("incomplete:options")
        for reason in quality.reasons
    )
    assert any(
        reason.startswith("freshness_unverified:options")
        for reason in quality.reasons
    )
