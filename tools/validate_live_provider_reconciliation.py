from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from dashboard.dashboard_controller import DashboardController
from dashboard.live_provider_reconciliation import build_raw_provider_reconciliation


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate raw INDMoney option quotes against one canonical live cycle."
    )
    parser.add_argument("--symbol", default="NIFTY")
    parser.add_argument("--levels", type=int, default=5)
    args = parser.parse_args()

    dashboard = DashboardController()
    provider = dashboard.runtime.get_provider()
    captured = {}
    original_get_quotes = provider.get_quotes

    def capture_quotes(security_ids):
        quotes = original_get_quotes(security_ids)
        captured["quotes"] = dict(quotes or {})
        captured["requested_ids"] = [int(value) for value in security_ids]
        return quotes

    provider.get_quotes = capture_quotes
    try:
        dashboard.load(symbol=args.symbol, levels=args.levels)
    finally:
        provider.get_quotes = original_get_quotes

    ctx = dashboard.runtime.get_context()
    report = build_raw_provider_reconciliation(captured.get("quotes", {}), ctx)

    print(json.dumps(report, indent=2, default=str))
    print(f"LIVE_PROVIDER_RECONCILIATION={report['status']}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
