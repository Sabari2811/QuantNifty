from datetime import datetime, timezone
from types import SimpleNamespace

from dashboard.components.header import _acquisition_time
from core.data_provenance import AcquisitionProvenance, RuntimeDataProvenance


def test_header_uses_latest_canonical_acquisition_time():
    spot_time = datetime(2026, 8, 26, 1, 0, tzinfo=timezone.utc)
    option_time = datetime(2026, 8, 26, 1, 5, tzinfo=timezone.utc)
    candle_time = datetime(2026, 8, 26, 1, 2, tzinfo=timezone.utc)

    dashboard = SimpleNamespace(
        data_provenance=RuntimeDataProvenance(
            spot=AcquisitionProvenance(source="spot", acquired_at=spot_time),
            option_chain=AcquisitionProvenance(source="options", acquired_at=option_time),
            candles=AcquisitionProvenance(source="candles", acquired_at=candle_time),
        )
    )

    assert _acquisition_time(dashboard) == option_time


def test_header_returns_no_timestamp_when_provenance_is_unavailable():
    dashboard = SimpleNamespace(data_provenance=RuntimeDataProvenance())

    assert _acquisition_time(dashboard) is None
