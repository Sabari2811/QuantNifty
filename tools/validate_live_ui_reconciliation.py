"""Run a fresh live DashboardData cycle and print backend -> UI reconciliation.

This is intentionally outside pytest: it requires a live INDMoney session.
"""

from __future__ import annotations

import argparse
import json

from dashboard.dashboard_controller import DashboardController
from dashboard.live_reconciliation import build_live_reconciliation


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", default="NIFTY")
    parser.add_argument("--levels", type=int, default=5)
    args = parser.parse_args()

    dashboard = DashboardController().load(args.symbol, args.levels)
    report = build_live_reconciliation(dashboard)

    print(json.dumps(report, indent=2, default=str))

    if report["gaps"]:
        print("RECONCILIATION=GAP")
        return 2

    print("RECONCILIATION=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
