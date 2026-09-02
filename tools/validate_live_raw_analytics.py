from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from dashboard.dashboard_controller import DashboardController
from dashboard.live_raw_analytics_reconciliation import reconcile_raw_quote_analytics


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate quote-derived live analytics directly against captured provider quotes."
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
        return quotes

    provider.get_quotes = capture_quotes
    try:
        dashboard.load(symbol=args.symbol, levels=args.levels)
    finally:
        provider.get_quotes = original_get_quotes

    ctx = dashboard.runtime.get_context()
    report = reconcile_raw_quote_analytics(
        captured.get("quotes", {}),
        ctx.option_chain,
        ctx.spot,
        ctx.analytics or {},
    )

    print(json.dumps(report, indent=2, default=str))
    print(f"LIVE_RAW_ANALYTICS={report['status']}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
