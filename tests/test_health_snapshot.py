from datetime import datetime, timezone
from types import SimpleNamespace

from core.data_provenance import AcquisitionProvenance, RuntimeDataProvenance
from monitoring.health import build_health_snapshot, health_as_dict


def test_health_snapshot_preserves_freshness_integrity_and_execution_status():
    provenance = RuntimeDataProvenance(
        option_chain=AcquisitionProvenance(
            source="INDstocks",
            expected_count=10,
            received_count=10,
            missing_count=0,
            freshness_verified=True,
            provider_timestamp=datetime.now(timezone.utc),
            integrity_status="VALID",
        )
    )
    execution_result = SimpleNamespace(status=SimpleNamespace(value="EXECUTED"))
    dashboard = SimpleNamespace(
        provider="INDstocks",
        runtime_status="READY",
        data_provenance=provenance,
        option_chain_integrity={"status": "VALID"},
        execution_result=execution_result,
        cycle_no=12,
    )

    snapshot = build_health_snapshot(dashboard)

    assert snapshot.provider == "INDstocks"
    assert snapshot.runtime_status == "READY"
    assert snapshot.data_freshness == "VERIFIED"
    assert snapshot.option_chain_integrity == "VALID"
    assert snapshot.execution_status == "EXECUTED"
    assert snapshot.cycle_no == 12


def test_health_snapshot_fails_closed_when_runtime_provenance_is_missing():
    dashboard = SimpleNamespace(
        provider="INDstocks",
        runtime_status="UNAVAILABLE",
        data_provenance=None,
        option_chain_integrity=None,
        execution_result=None,
        cycle_no=0,
    )

    result = health_as_dict(dashboard)

    assert result == {
        "provider": "INDstocks",
        "runtime_status": "UNAVAILABLE",
        "data_freshness": "UNAVAILABLE",
        "option_chain_integrity": "UNAVAILABLE",
        "execution_status": "NOT_AVAILABLE",
        "cycle_no": 0,
    }
