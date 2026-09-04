"""Inspect the exact contracts responsible for live option-chain integrity findings."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from dashboard.dashboard_controller import DashboardController


def _finite(value: Any) -> float | None:
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None
    return value if value == value else None


def _timestamp_age(timestamp, acquired_at):
    if timestamp is None or acquired_at is None:
        return None
    try:
        return max(0.0, (acquired_at - timestamp).total_seconds())
    except (TypeError, ValueError):
        return None


def _contract_diagnostics(chain, spot: float, contract_reasons):
    rows = []
    timestamps = {} if chain is None else chain.attrs.get("option_quote_timestamps", {})
    provenance = chain.attrs.get("data_provenance") if chain is not None else None
    acquired_at = getattr(provenance, "acquired_at", None)
    for key, reasons in contract_reasons:
        row_number = None
        marker = "|row:"
        if marker in key:
            try:
                row_number = int(key.rsplit(marker, 1)[1])
            except ValueError:
                row_number = None
        if row_number is None or row_number >= len(chain):
            rows.append({"contract": key, "reasons": list(reasons)})
            continue
        row = chain.reset_index(drop=True).iloc[row_number]
        strike = _finite(row.get("Strike"))
        item = {
            "contract": key,
            "reasons": list(reasons),
            "strike": strike,
            "spot": spot,
        }
        for option_type in ("CE", "PE"):
            ltp = _finite(row.get(f"{option_type}_LTP"))
            intrinsic = None
            if strike is not None and spot is not None:
                intrinsic = max(spot - strike, 0.0) if option_type == "CE" else max(strike - spot, 0.0)
            security_id = row.get(f"{option_type}_ID")
            timestamp = timestamps.get(str(security_id))
            item[option_type.lower()] = {
                "id": security_id,
                "ltp": ltp,
                "intrinsic": intrinsic,
                "shortfall_below_intrinsic": None if intrinsic is None or ltp is None else max(intrinsic - ltp, 0.0),
                "provider_timestamp": timestamp,
                "provider_timestamp_age_seconds": _timestamp_age(timestamp, acquired_at),
                "oi": row.get(f"{option_type}_OI"),
                "volume": row.get(f"{option_type}_VOLUME"),
            }
        rows.append(item)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect live option-chain integrity findings.")
    parser.add_argument("--symbol", default="NIFTY")
    parser.add_argument("--levels", type=int, default=5)
    args = parser.parse_args()

    if not 2 <= args.levels <= 10:
        parser.error("--levels must be an integer between 2 and 10")

    controller = DashboardController()
    dashboard = controller.load(args.symbol, args.levels)
    ctx = controller.runtime.get_context()
    chain = ctx.option_chain
    report = dashboard.option_chain_integrity or {}
    spot = _finite(ctx.spot)
    contract_reasons = report.get("contract_reasons", ())

    evidence = {
        "symbol": args.symbol,
        "cycle_no": ctx.cycle_no,
        "spot": spot,
        "runtime_status": ctx.runtime_status,
        "trade_status": ctx.trade_status,
        "integrity": report,
        "option_chain_provenance": None if ctx.data_provenance is None or ctx.data_provenance.option_chain is None else ctx.data_provenance.option_chain.as_dict(),
        "contracts": _contract_diagnostics(chain, spot, contract_reasons) if chain is not None else [],
    }
    print(json.dumps(evidence, indent=2, default=str))
    print(f"LIVE_OPTION_CHAIN_INTEGRITY={report.get('status', 'UNAVAILABLE')}")
    return 0 if report.get("status") in {"VALID", "SUSPECT", "INVALID"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
