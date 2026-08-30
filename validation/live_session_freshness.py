from __future__ import annotations


def evaluate_consecutive_freshness(cycles: list[dict]) -> dict:
    """Evaluate timestamp evidence for live spot/option-chain acquisitions.

    Historical candles are intentionally excluded. Every requested cycle must
    contain timestamp-bearing, non-stale live quote evidence for both sources.
    """
    required_sources = ("spot", "option_chain")
    timestamped_cycles = 0
    unverified_items = 0
    stale_items = 0
    missing_items = 0

    for cycle in cycles:
        cycle_timestamped = True
        for source in required_sources:
            item = cycle.get(source)
            if not item:
                missing_items += 1
                cycle_timestamped = False
                continue
            if item.get("provider_timestamp") is None or item.get("freshness_status") in {"UNVERIFIED", "REALTIME_UNTIMESTAMPED"}:
                unverified_items += 1
                cycle_timestamped = False
            if item.get("freshness_status") == "STALE":
                stale_items += 1
                cycle_timestamped = False
        if cycle_timestamped:
            timestamped_cycles += 1

    if stale_items:
        status = "FAIL"
    elif missing_items or unverified_items or timestamped_cycles != len(cycles):
        status = "NOT_VERIFIED"
    else:
        status = "PASS"

    return {
        "status": status,
        "cycles": len(cycles),
        "timestamped_cycles": timestamped_cycles,
        "missing_items": missing_items,
        "unverified_items": unverified_items,
        "stale_items": stale_items,
    }
