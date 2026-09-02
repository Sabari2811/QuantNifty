from __future__ import annotations

import argparse
import json

from dashboard.dashboard_controller import DashboardController
from dashboard.live_reconciliation import reconcile_dashboard_cycle


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate one live DashboardData cycle against canonical runtime context.")
    parser.add_argument("--symbol", default="NIFTY")
    parser.add_argument("--levels", type=int, default=5)
    args = parser.parse_args()

    dashboard = DashboardController()
    data = dashboard.load(symbol=args.symbol, levels=args.levels)
    ctx = dashboard.runtime.get_context()
    report = reconcile_dashboard_cycle(ctx, data)

    print(json.dumps(report, indent=2, default=str))
    print(f"LIVE_DASHBOARD_RECONCILIATION={report['status']}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
