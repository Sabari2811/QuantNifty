from __future__ import annotations

from core.data_provenance import AcquisitionProvenance, RuntimeDataProvenance


def adapt_provenance(provenance: RuntimeDataProvenance | None) -> dict:
    """Expose canonical backend provenance without collapsing independent states."""
    if provenance is None:
        provenance = RuntimeDataProvenance()

    def adapt(item: AcquisitionProvenance | None) -> dict | None:
        if item is None:
            return None
        return {
            "source": item.source,
            "acquired_at": item.acquired_at,
            "provider_timestamp": item.provider_timestamp,
            "expected_count": item.expected_count,
            "received_count": item.received_count,
            "missing_count": item.missing_count,
            "coverage_ratio": item.coverage_ratio,
            "coverage_status": item.coverage_status,
            "freshness_status": item.freshness_status,
            "freshness_verified": item.freshness_verified,
            "freshness_seconds": item.freshness_seconds,
            "integrity_status": item.integrity_status,
            "integrity_reasons": item.integrity_reasons,
            "status": item.status,
            "reasons": item.reasons,
        }

    return {
        "spot": adapt(provenance.spot),
        "option_chain": adapt(provenance.option_chain),
        "candles": adapt(provenance.candles),
        "coverage_ratio": provenance.coverage_ratio,
        "complete": provenance.complete,
    }
