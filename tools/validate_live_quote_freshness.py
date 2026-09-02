"""Validate consecutive timestamp-bearing INDstocks WebSocket quotes.

This is intentionally a live-session tool, not a pytest test. It keeps one
WebSocket session open and captures receive time immediately after each
bounded recv_tick() call so provider timestamp age can be assessed without
reconstructing receive time later.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from providers.indmoney_websocket import (
    IndmoneyPriceFeed,
    assess_quote_freshness,
)


def validate_consecutive_quotes(
    access_token: str,
    instrument: str,
    *,
    cycles: int = 5,
    timeout: float = 10.0,
    pause_seconds: float = 0.0,
    max_age_ms: int = 2000,
    max_clock_skew_ms: int = 2000,
) -> tuple[list[dict], dict[str, bool]]:
    if cycles < 1:
        raise ValueError("cycles must be >= 1")
    if timeout <= 0:
        raise ValueError("timeout must be > 0")
    if pause_seconds < 0:
        raise ValueError("pause_seconds must be >= 0")

    observations: list[dict] = []
    with IndmoneyPriceFeed(access_token, timeout=timeout) as feed:
        connected_at = datetime.now(timezone.utc)
        feed.subscribe([instrument], mode="ltp")
        for cycle in range(1, cycles + 1):
            tick = feed.recv_tick()
            received_at = datetime.now(timezone.utc)
            if tick is None:
                observations.append({
                    "cycle": cycle,
                    "received_at": received_at.isoformat(),
                    "status": "NO_TICK",
                })
            else:
                freshness = assess_quote_freshness(
                    tick,
                    received_at=received_at,
                    max_age_ms=max_age_ms,
                    max_clock_skew_ms=max_clock_skew_ms,
                )
                observations.append({
                    "cycle": cycle,
                    "instrument": tick.instrument,
                    "mode": tick.mode,
                    "ltp": tick.ltp,
                    "provider_timestamp": freshness.provider_timestamp.isoformat(),
                    "provider_timestamp_ms": tick.timestamp_ms,
                    "received_at": freshness.received_at.isoformat(),
                    "transport_age_ms": freshness.transport_age_ms,
                    "clock_skew_ms": freshness.clock_skew_ms,
                    "freshness_status": freshness.status,
                })
            if cycle < cycles and pause_seconds:
                time.sleep(pause_seconds)

    valid = [item for item in observations if item.get("freshness_status")]
    statuses = [item["freshness_status"] for item in valid]
    timestamps = [item["provider_timestamp_ms"] for item in valid]
    checks = {
        "connected": connected_at is not None,
        "all_cycles_received": len(valid) == cycles,
        "all_quotes_fresh_or_bounded_skew": bool(valid)
        and all(status in {"fresh", "fresh_with_clock_skew"} for status in statuses),
        "no_excessive_clock_skew": bool(valid)
        and all(item["clock_skew_ms"] <= max_clock_skew_ms for item in valid),
        "provider_timestamps_monotonic": len(timestamps) == cycles
        and all(current > previous for previous, current in zip(timestamps, timestamps[1:])),
    }
    return observations, checks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--instrument", default="NIDX:40000001")
    parser.add_argument("--cycles", type=int, default=5)
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--pause-seconds", type=float, default=0.0)
    parser.add_argument("--max-age-ms", type=int, default=2000)
    parser.add_argument("--max-clock-skew-ms", type=int, default=2000)
    args = parser.parse_args()

    token = os.getenv("INDSTOCKS_API_TOKEN")
    if not token:
        print("INDSTOCKS_API_TOKEN is required; token value is never printed.", file=sys.stderr)
        return 2

    try:
        observations, checks = validate_consecutive_quotes(
            token,
            args.instrument,
            cycles=args.cycles,
            timeout=args.timeout,
            pause_seconds=args.pause_seconds,
            max_age_ms=args.max_age_ms,
            max_clock_skew_ms=args.max_clock_skew_ms,
        )
    except Exception as exc:
        print(f"LIVE_QUOTE_FRESHNESS=ERROR | {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2

    print(json.dumps({"instrument": args.instrument, "observations": observations, "checks": checks}, indent=2))
    failed = [name for name, value in checks.items() if value is False]
    if failed:
        print("LIVE_QUOTE_FRESHNESS=GAP")
        print("FAILED_CHECKS=" + ",".join(failed))
        return 2
    print("LIVE_QUOTE_FRESHNESS=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
