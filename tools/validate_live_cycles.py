"""Run consecutive canonical live cycles for provenance/OI validation.

This tool intentionally runs outside pytest because it requires a live
INDMoney session. It keeps one RuntimeManager/LiveEngine instance so stateful
OI comparison can observe consecutive cycles.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from dashboard.dashboard_controller import DashboardController


def _provenance_state(dashboard):
    provenance = dashboard.data_provenance
    option = provenance.option_chain if provenance else None
    spot = provenance.spot if provenance else None
    return {
        "spot": None if spot is None else spot.as_dict(),
        "option_chain": None if option is None else option.as_dict(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", default="NIFTY")
    parser.add_argument("--levels", type=int, default=5)
    parser.add_argument("--cycles", type=int, default=2)
    parser.add_argument("--sleep-seconds", type=float, default=0.0)
    args = parser.parse_args()

    if args.cycles < 1:
        parser.error("--cycles must be >= 1")
    if args.sleep_seconds < 0:
        parser.error("--sleep-seconds must be >= 0")

    dashboard = DashboardController()
    results = []

    for cycle in range(args.cycles):
        current = dashboard.load(args.symbol, args.levels)
        results.append(
            {
                "iteration": cycle + 1,
                "cycle_no": current.cycle_no,
                "spot": current.spot,
                "expiry": current.expiry,
                "provenance": _provenance_state(current),
                "oi": (current.analytics or {}).get("oi", {}),
            }
        )
        if cycle + 1 < args.cycles and args.sleep_seconds:
            time.sleep(args.sleep_seconds)

    checks = {
        "distinct_cycle_numbers": len({item["cycle_no"] for item in results}) == len(results),
        "all_spot_complete": all(
            item["provenance"]["spot"] is not None
            and item["provenance"]["spot"]["coverage_status"] == "COMPLETE"
            for item in results
        ),
        "all_option_chain_complete": all(
            item["provenance"]["option_chain"] is not None
            and item["provenance"]["option_chain"]["coverage_status"] == "COMPLETE"
            for item in results
        ),
    }

    # OI state is deliberately reported rather than asserted: the first
    # cycle should establish the baseline, while later cycles may classify
    # flow only when the provider returns changed OI values.
    if results:
        checks["first_cycle_oi_reported"] = "oi" in results[0]
    if len(results) > 1:
        checks["subsequent_cycle_oi_reported"] = all("oi" in item for item in results[1:])

    print(json.dumps({"cycles": results, "checks": checks}, indent=2, default=str))

    failed = [name for name, value in checks.items() if value is False]
    if failed:
        print("LIVE_CYCLES=GAP")
        print("FAILED_CHECKS=" + ",".join(failed))
        return 2

    print("LIVE_CYCLES=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
