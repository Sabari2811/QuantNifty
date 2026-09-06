from __future__ import annotations

from core.data_provenance import AcquisitionProvenance, RuntimeDataProvenance


def option_chain_quality_state(option_chain: dict | None) -> str:
    """Return presentation quality without collapsing canonical provenance states."""
    if not option_chain:
        return "UNAVAILABLE"

    coverage_status = option_chain.get("coverage_status")
    integrity_status = option_chain.get("integrity_status")

    if coverage_status is None or integrity_status is None:
        return "UNAVAILABLE"
    if coverage_status != "COMPLETE" or integrity_status in ("SUSPECT", "INVALID"):
        return "DEGRADED"
    return "READY"


def adapt_provenance(provenance: RuntimeDataProvenance | None) -> dict:
    """Expose canonical backend provenance without collapsing independent states.

    A missing runtime provenance object remains unavailable rather than being
    replaced with a synthetic default provenance model.
    """
    if provenance is None:
        return {
            "spot": None,
            "option_chain": None,
            "option_chain_quality": "UNAVAILABLE",
            "candles": None,
            "coverage_ratio": None,
            "complete": False,
        }

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

    option_chain = adapt(getattr(provenance, "option_chain", None))
    option_chain_quality = option_chain_quality_state(option_chain)

    return {
        "spot": adapt(getattr(provenance, "spot", None)),
        "option_chain": option_chain,
        "option_chain_quality": option_chain_quality,
        "candles": adapt(getattr(provenance, "candles", None)),
        "coverage_ratio": getattr(provenance, "coverage_ratio", None),
        "complete": getattr(provenance, "complete", False),
    }
