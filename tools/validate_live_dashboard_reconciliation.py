from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


# Allow direct execution from the repository's tools/ directory:
#   python tools/validate_live_dashboard_reconciliation.py
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from dashboard.dashboard_controller import DashboardController
from dashboard.live_reconciliation import build_live_reconciliation


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate one live DashboardData cycle against canonical UI adapters/components.")
    parser.add_argument("--symbol", default="NIFTY")
    parser.add_argument("--levels", type=int, default=5)
    args = parser.parse_args()

    dashboard = DashboardController()
    data = dashboard.load(symbol=args.symbol, levels=args.levels)
    report = build_live_reconciliation(data)

    print(json.dumps(report, indent=2, default=str))
    print(f"LIVE_DASHBOARD_RECONCILIATION={report['field_status']}")
    return 0 if report["field_status"] == "MATCH" else 1


if __name__ == "__main__":
    raise SystemExit(main())
