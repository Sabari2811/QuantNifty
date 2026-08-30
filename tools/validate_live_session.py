"""Validate consecutive live DashboardData cycles.

This tool intentionally runs outside pytest because it requires a live INDMoney
session. It reuses the singleton RuntimeManager so OI state is preserved between
cycles and evaluates the canonical backend -> UI reconciliation on every cycle.
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
from dashboard.live_reconciliation import build_live_reconciliation


def _provenance_summary(dashboard):
    provenance = dashboard.data_provenance
    result = {}
    for name in ("spot", "option_chain", "candles"):
        item = getattr(provenance, name, None)
        result[name] = None if item is None else item.as_dict()
    return result


def _oi_summary(dashboard):
    analytics = dashboard.analytics or {}
    oi = analytics.get("oi")
    if oi is None:
        return None
    if hasattr(oi, "as_dict"):
        return oi.as_dict()
    return oi


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", default="NIFTY")
    parser.add_argument("--levels", type=int, default=5)
    parser.add_argument("--cycles", type=int, default=3)
    parser.add_argument("--interval", type=float, default=30.0)
    args = parser.parse_args()

    if args.cycles < 2:
        parser.error("--cycles must be at least 2 to validate consecutive-cycle state")
    if args.interval < 0:
        parser.error("--interval must be non-negative")

    controller = DashboardController()
    reports = []
    failures = []

    for cycle_index in range(args.cycles):
        dashboard = controller.load(args.symbol, args.levels)
        report = build_live_reconciliation(dashboard)
        provenance = _provenance_summary(dashboard)
        oi = _oi_summary(dashboard)

        cycle = {
            "cycle": cycle_index + 1,
            "cycle_no": dashboard.cycle_no,
            "spot": dashboard.spot,
            "expiry": dashboard.expiry,
            "field_status": report["field_status"],
            "gaps": report["gaps"],
            "option_chain": report["option_chain"],
            "decision": report["decision"],
            "intelligence": report["intelligence"],
            "provenance": provenance,
            "oi": oi,
        }
        reports.append(cycle)

        if report["gaps"]:
            failures.append({"cycle": cycle_index + 1, "type": "reconciliation", "gaps": report["gaps"]})

        for source, item in provenance.items():
            if item is None:
                failures.append({"cycle": cycle_index + 1, "type": "missing_provenance", "source": source})
                continue
            if item.get("coverage_status") == "INCOMPLETE":
                failures.append({"cycle": cycle_index + 1, "type": "incomplete_coverage", "source": source})
            if item.get("status") == "INVALID":
                failures.append({"cycle": cycle_index + 1, "type": "invalid_provenance", "source": source})

        if cycle_index + 1 < args.cycles and args.interval:
            time.sleep(args.interval)

    print(json.dumps({
        "symbol": args.symbol,
        "levels": args.levels,
        "cycles_requested": args.cycles,
        "cycles_completed": len(reports),
        "failures": failures,
        "cycles": reports,
    }, indent=2, default=str))

    if failures:
        print("LIVE_SESSION_VALIDATION=FAIL")
        return 2

    print("LIVE_SESSION_VALIDATION=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
