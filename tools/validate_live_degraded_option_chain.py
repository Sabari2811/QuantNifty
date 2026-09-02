"""Validate fail-closed behavior against one real live option-chain response.

The tool performs a normal authenticated live cycle, then removes exactly one
contract from the provider response in-memory before the canonical
OptionChainManager consumes it. No provider state or order state is changed.
The goal is to prove that a real acquisition path degrades to PARTIAL/INVALID
and that Greeks, analytics, intelligence, and trade execution are blocked.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from dashboard.dashboard_controller import DashboardController


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", default="NIFTY")
    parser.add_argument("--levels", type=int, default=2)
    args = parser.parse_args()

    if not 2 <= args.levels <= 10:
        parser.error("--levels must be an integer between 2 and 10")

    dashboard = DashboardController()
    provider = dashboard.runtime.get_provider()
    original_get_quotes = provider.get_quotes
    observed = {}

    def degraded_get_quotes(security_ids):
        quotes = original_get_quotes(security_ids)
        observed["requested"] = list(security_ids)
        observed["received_before_degradation"] = len(quotes)
        if not quotes:
            return quotes
        first_id = security_ids[0]
        quotes.pop(f"NFO_{first_id}", None)
        observed["removed_security_id"] = first_id
        observed["received_after_degradation"] = len(quotes)
        return quotes

    provider.get_quotes = degraded_get_quotes
    try:
        current = dashboard.load(args.symbol, args.levels)
    finally:
        provider.get_quotes = original_get_quotes

    provenance = current.data_provenance
    option = provenance.option_chain if provenance else None
    integrity = current.option_chain_integrity or {}

    checks = {
        "real_provider_response_observed": observed.get("received_before_degradation", 0) > 0,
        "exactly_one_contract_removed": (
            observed.get("received_before_degradation", 0) - observed.get("received_after_degradation", 0) == 1
        ),
        "coverage_partial": option is not None and option.coverage_status == "PARTIAL",
        "provenance_incomplete": option is not None and option.complete is False,
        "integrity_invalid": integrity.get("status") == "INVALID",
        "runtime_degraded": current.runtime_status == "DEGRADED",
        "trade_blocked": current.trade_status == "BLOCKED",
        "analytics_not_computed": current.analytics == {},
        "greeks_not_computed": current.greeks is None,
        "decision_not_computed": current.signal == {} and current.trade_plan == {},
        "intelligence_not_computed": current.intelligence is None,
    }

    evidence = {
        "symbol": args.symbol,
        "levels": args.levels,
        "observed": observed,
        "runtime_status": current.runtime_status,
        "trade_status": current.trade_status,
        "trade_block_reason": current.trade_block_reason,
        "option_chain_provenance": None if option is None else option.as_dict(),
        "option_chain_integrity": integrity,
        "checks": checks,
    }
    print(json.dumps(evidence, indent=2, default=str))

    failed = [name for name, value in checks.items() if value is False]
    if failed:
        print("LIVE_DEGRADED=GAP")
        print("FAILED_CHECKS=" + ",".join(failed))
        return 2

    print("LIVE_DEGRADED=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
