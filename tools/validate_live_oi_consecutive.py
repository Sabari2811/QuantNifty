from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from dashboard.dashboard_controller import DashboardController


def _expected_flow(price_change, oi_change):
    if pd.isna(price_change) or pd.isna(oi_change):
        return "UNKNOWN"
    if price_change == 0 and oi_change == 0:
        return "NO_CHANGE"
    if price_change > 0 and oi_change > 0:
        return "LONG_BUILDUP"
    if price_change <= 0 and oi_change > 0:
        return "SHORT_BUILDUP"
    if price_change > 0 and oi_change <= 0:
        return "SHORT_COVERING"
    return "LONG_UNWINDING"


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate consecutive live OI flow classification.")
    parser.add_argument("--symbol", default="NIFTY")
    parser.add_argument("--levels", type=int, default=5)
    args = parser.parse_args()

    dashboard = DashboardController()
    first = dashboard.load(args.symbol, args.levels)
    first_ctx = dashboard.runtime.get_context()
    first_chain = first_ctx.greeks.copy(deep=True)

    second = dashboard.load(args.symbol, args.levels)
    second_ctx = dashboard.runtime.get_context()
    second_chain = second_ctx.greeks.copy(deep=True)
    oi_result = second_ctx.analytics.get("oi_flow", {})
    table = oi_result.get("table", pd.DataFrame())

    if table.empty:
        print(json.dumps({"status": "GAP", "reason": "oi_table_missing"}, indent=2))
        print("LIVE_OI_CONSECUTIVE=GAP")
        return 1

    previous = first_chain[["Strike", "CE_LTP", "CE_OI", "PE_LTP", "PE_OI"]].copy()
    current = second_chain[["Strike", "CE_LTP", "CE_OI", "PE_LTP", "PE_OI"]].copy()
    merged = current.merge(previous, on="Strike", how="left", suffixes=("", "_PREV"), indicator=True)

    checks = []
    gaps = []
    for row_no, row in merged.iterrows():
        matched = row["_merge"] == "both"
        for side in ("CE", "PE"):
            price_change = None if not matched else row[f"{side}_LTP"] - row[f"{side}_LTP_PREV"]
            oi_change = None if not matched else row[f"{side}_OI"] - row[f"{side}_OI_PREV"]
            expected = _expected_flow(price_change, oi_change)
            actual = table.iloc[row_no][f"{side}_FLOW"] if row_no < len(table) else None
            passed = expected == actual
            checks.append({
                "strike": row["Strike"],
                "side": side,
                "price_change": price_change,
                "oi_change": oi_change,
                "expected": expected,
                "actual": actual,
                "status": "PASS" if passed else "MISMATCH",
            })
            if not passed:
                gaps.append(f"strike:{row['Strike']}|side:{side}|expected:{expected}|actual:{actual}")

    report = {
        "status": "PASS" if not gaps else "GAP",
        "first_cycle": first_ctx.cycle_no,
        "second_cycle": second_ctx.cycle_no,
        "first_rows": len(first_chain),
        "second_rows": len(second_chain),
        "oi_status": oi_result.get("summary", {}).get("status"),
        "checks": checks,
        "gaps": gaps,
    }
    print(json.dumps(report, indent=2, default=str))
    print(f"LIVE_OI_CONSECUTIVE={report['status']}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
