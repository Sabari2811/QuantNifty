"""Canonical runtime health snapshot helpers for observability."""

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class HealthSnapshot:
    provider: str
    runtime_status: str
    data_freshness: str
    option_chain_integrity: str
    execution_status: str
    cycle_no: int


def build_health_snapshot(dashboard: Any) -> HealthSnapshot:
    provenance = getattr(dashboard, "data_provenance", None)
    option_chain = getattr(provenance, "option_chain", None) if provenance else None
    freshness = getattr(option_chain, "freshness_status", None) or "UNAVAILABLE"

    integrity = getattr(dashboard, "option_chain_integrity", None)
    if isinstance(integrity, dict):
        integrity_status = integrity.get("status") or integrity.get("integrity_status") or "UNAVAILABLE"
    else:
        integrity_status = "UNAVAILABLE"

    execution_result = getattr(dashboard, "execution_result", None)
    execution_status = getattr(execution_result, "status", None)
    execution_status = getattr(execution_status, "value", execution_status) or "NOT_AVAILABLE"

    return HealthSnapshot(
        provider=str(getattr(dashboard, "provider", "") or "UNKNOWN"),
        runtime_status=str(getattr(dashboard, "runtime_status", "") or "UNKNOWN"),
        data_freshness=str(freshness),
        option_chain_integrity=str(integrity_status),
        execution_status=str(execution_status),
        cycle_no=int(getattr(dashboard, "cycle_no", 0) or 0),
    )


def health_as_dict(dashboard: Any) -> dict[str, Any]:
    """Return a serializable health view without deriving trading decisions."""
    return asdict(build_health_snapshot(dashboard))
