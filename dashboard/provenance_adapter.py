from __future__ import annotations

from core.data_provenance import AcquisitionProvenance, RuntimeDataProvenance


def adapt_provenance(provenance: RuntimeDataProvenance | None) -> dict:
    """Expose canonical backend provenance without collapsing independent states.

    The adapter is also safe for lightweight dashboard test doubles that only
    provide a subset of provenance attributes.
    """
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

    option_chain = adapt(getattr(provenance, "option_chain", None))

    # This is presentation state only. It does not replace or merge the
    # independent canonical coverage/integrity fields above.
    if option_chain is None:
        option_chain_quality = "UNAVAILABLE"
    elif (
        option_chain["coverage_status"] != "COMPLETE"
        or option_chain["integrity_status"] in ("SUSPECT", "INVALID")
    ):
        option_chain_quality = "DEGRADED"
    else:
        option_chain_quality = "READY"

    return {
        "spot": adapt(getattr(provenance, "spot", None)),
        "option_chain": option_chain,
        "option_chain_quality": option_chain_quality,
        "candles": adapt(getattr(provenance, "candles", None)),
        "coverage_ratio": getattr(provenance, "coverage_ratio", 0.0),
        "complete": getattr(provenance, "complete", False),
    }
