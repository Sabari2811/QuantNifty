"""Run one fresh live cycle and report canonical backend -> DashboardData gaps."""

from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from dashboard.dashboard_controller import DashboardController
from dashboard.live_reconciliation import reconcile_dashboard_cycle


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", default="NIFTY")
    parser.add_argument("--levels", type=int, default=5)
    args = parser.parse_args()

    dashboard = DashboardController()
    data = dashboard.load(args.symbol, args.levels)
    ctx = dashboard.runtime.get_context()
    report = reconcile_dashboard_cycle(ctx, data)
    report["runtime"] = {
        "symbol": ctx.symbol,
        "cycle_no": ctx.cycle_no,
        "runtime_status": ctx.runtime_status,
        "trade_status": ctx.trade_status,
        "trade_block_reason": ctx.trade_block_reason,
    }
    print(json.dumps(report, indent=2, default=str))
    print(f"LIVE_DASHBOARD_RECONCILIATION={report['status']}")
    return 0 if report["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
