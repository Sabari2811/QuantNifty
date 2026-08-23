from datetime import datetime, timezone

import pandas as pd

from core.data_provenance import AcquisitionProvenance
from recording.snapshot_recorder import SnapshotRecorder


def test_dataframe_provenance_attrs_are_parquet_serializable(tmp_path):
    acquired_at = datetime.now(timezone.utc)
    provenance = AcquisitionProvenance(
        source="test",
        acquired_at=acquired_at,
        expected_count=2,
        received_count=2,
        missing_count=0,
    )

    frame = pd.DataFrame({"value": [1, 2]})
    frame.attrs["data_provenance"] = provenance

    path = tmp_path / "option_chain.parquet"
    SnapshotRecorder()._save_dataframe(path, frame)

    restored = pd.read_parquet(path)

    assert restored.attrs["data_provenance"]["source"] == "test"
    assert restored.attrs["data_provenance"]["expected_count"] == 2
    assert restored.attrs["data_provenance"]["received_count"] == 2
    assert restored.attrs["data_provenance"]["acquired_at"] == acquired_at.isoformat()
