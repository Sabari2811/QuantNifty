"""Validate consecutive live DashboardData cycles and persist evidence.

This tool intentionally runs outside pytest because it requires a live INDMoney
session. It reuses the singleton RuntimeManager so OI state is preserved between
cycles and evaluates the canonical backend -> UI reconciliation on every cycle.

The complete machine-readable report and concise summary are written under
``validation/``. Stdout intentionally contains only the final gate status.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from dashboard.dashboard_controller import DashboardController
from dashboard.live_reconciliation import build_live_reconciliation

DEFAULT_REPORT = os.path.join(PROJECT_ROOT, "validation", "live_session_latest.json")
DEFAULT_SUMMARY = os.path.join(PROJECT_ROOT, "validation", "live_session_latest_summary.txt")


def _provenance_summary(dashboard):
    provenance = dashboard.data_provenance
    result = {}
    for name in ("spot", "option_chain", "candles"):
        item = getattr(provenance, name, None) if provenance is not None else None
        result[name] = None if item is None else item.as_dict()
    return result


def _oi_summary(dashboard):
    analytics = dashboard.analytics or {}
    oi = analytics.get("oi_flow")
    if oi is None:
        # Backward-compatible read for older runtime artifacts; live output
        # should use the canonical oi_flow key.
        oi = analytics.get("oi")
    if oi is None:
        return None
    if hasattr(oi, "as_dict"):
        return oi.as_dict()
    return oi


def _ensure_parent(path: str) -> None:
    parent = os.path.dirname(os.path.abspath(path))
    if parent:
        os.makedirs(parent, exist_ok=True)


def _write_report(path: str, payload: dict) -> None:
    _ensure_parent(path)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, default=str)
        handle.write("\n")


def _write_summary(path: str, payload: dict) -> None:
    _ensure_parent(path)
    failures = payload["failures"]
    cycles = payload["cycles"]
    gates = payload["gates"]
    lines = [
        "QuantNifty Live Session Validation",
        "=================================",
        f"Generated UTC: {payload['generated_at_utc']}",
        f"Symbol: {payload['symbol']}",
        f"Levels: {payload['levels']}",
        f"Cycles requested: {payload['cycles_requested']}",
        f"Cycles completed: {payload['cycles_completed']}",
        "",
        "Gates:",
    ]
    for name, gate in gates.items():
        lines.append(f"  {name}: {gate['status']} — {gate['detail']}")
    lines.extend([
        "",
        f"Reconciliation: {'PASS' if all(not c['gaps'] for c in cycles) else 'FAIL'}",
        f"Provenance: {'PASS' if not any(f['type'] in {'missing_provenance', 'incomplete_coverage', 'invalid_provenance'} for f in failures) else 'FAIL'}",
        f"Overall: {'PASS' if not failures else 'FAIL'}",
        f"Failures: {len(failures)}",
    ])
    if failures:
        lines.extend(["", "Failure details:"])
        for failure in failures:
            lines.append(json.dumps(failure, sort_keys=True, default=str))
    lines.extend(["", "Cycle summary:"])
    for cycle in cycles:
        lines.append(
            f"cycle={cycle['cycle']} cycle_no={cycle['cycle_no']} spot={cycle['spot']} "
            f"field_status={cycle['field_status']} gaps={len(cycle['gaps'])}"
        )
        for source, item in cycle["provenance"].items():
            if item is None:
                lines.append(f"  {source}: MISSING")
            else:
                lines.append(
                    f"  {source}: status={item.get('status')} coverage={item.get('coverage_status')} "
                    f"freshness={item.get('freshness_status')} integrity={item.get('integrity_status')}"
                )
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")


def _gate(status: str, detail: str) -> dict:
    return {"status": status, "detail": detail}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", default="NIFTY")
    parser.add_argument("--levels", type=int, default=5)
    parser.add_argument("--cycles", type=int, default=3)
    parser.add_argument("--interval", type=float, default=30.0)
    parser.add_argument("--output", default=DEFAULT_REPORT, help="Complete JSON evidence report")
    parser.add_argument("--summary-output", default=DEFAULT_SUMMARY, help="Concise validation summary")
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

    # Gates deliberately distinguish PASS from NOT_VERIFIED. A REST quote
    # without provider timestamps cannot prove freshness, and a SUSPECT quote
    # cannot be silently promoted to trusted data merely because coverage is
    # complete.
    all_cycles = reports
    freshness_items = [
        item for cycle in all_cycles for item in cycle["provenance"].values() if item is not None
    ]
    timestamped = [item for item in freshness_items if item.get("provider_timestamp") is not None]
    stale = [item for item in freshness_items if item.get("freshness_status") == "STALE"]
    suspect = [item for item in freshness_items if item.get("integrity_status") == "SUSPECT"]
    invalid = [item for item in freshness_items if item.get("integrity_status") == "INVALID"]

    oi_states = [cycle["oi"] for cycle in all_cycles if cycle["oi"] is not None]
    oi_ready = len(oi_states) >= 2 and all(
        isinstance(state, dict) and state.get("status") in {"READY", "NO_CHANGE"}
        for state in oi_states[1:]
    )

    gates = {
        "backend_ui_reconciliation": _gate(
            "PASS" if not any(c["gaps"] for c in all_cycles) else "FAIL",
            "all DashboardData → UI reconciliation fields matched" if not any(c["gaps"] for c in all_cycles) else "field-level gaps recorded",
        ),
        "coverage": _gate(
            "PASS" if not any(f["type"] == "incomplete_coverage" for f in failures) else "FAIL",
            "no incomplete acquisition coverage observed" if not any(f["type"] == "incomplete_coverage" for f in failures) else "incomplete coverage observed",
        ),
        "freshness": _gate(
            "PASS" if timestamped and not stale else "NOT_VERIFIED",
            "timestamp-bearing source observed with no stale state" if timestamped and not stale else "provider quote timestamp/market-session freshness evidence is insufficient",
        ),
        "integrity": _gate(
            "PASS" if not invalid and not suspect else "DEGRADED",
            "all observed sources passed integrity" if not invalid and not suspect else f"suspect={len(suspect)} invalid={len(invalid)}; degradation remains explicit",
        ),
        "oi_consecutive_state": _gate(
            "PASS" if oi_ready else "NOT_VERIFIED",
            "consecutive cycles reached READY/NO_CHANGE" if oi_ready else "insufficient consecutive OI evidence",
        ),
        "decision_intelligence": _gate(
            "PASS" if all(c["intelligence"]["status"] == "MATCH" for c in all_cycles) and all(
                "decision" not in c["gaps"] for c in all_cycles
            ) else "FAIL",
            "canonical decision/intelligence values matched UI" if all(c["intelligence"]["status"] == "MATCH" for c in all_cycles) else "decision/intelligence mismatch recorded",
        ),
        "analytics_raw_reconciliation": _gate(
            "NOT_VERIFIED",
            "requires a fresh market-session raw-provider numerical reconciliation; successful analytics generation alone is not proof",
        ),
        "degraded_data_ui": _gate(
            "NOT_VERIFIED" if not suspect else "OBSERVED",
            "requires a controlled missing/invalid-data UI session" if not suspect else "live suspect integrity state observed; controlled UI degradation test still required",
        ),
    }

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "symbol": args.symbol,
        "levels": args.levels,
        "cycles_requested": args.cycles,
        "cycles_completed": len(reports),
        "failures": failures,
        "gates": gates,
        "cycles": reports,
    }

    _write_report(args.output, payload)
    _write_summary(args.summary_output, payload)

    blocking_failures = failures
    print("QuantNifty Live Validation")
    print("───────────────────────────")
    print(f"Cycles:          {len(reports)}/{args.cycles}")
    print(f"Reconciliation:  {gates['backend_ui_reconciliation']['status']}")
    print(f"Coverage:        {gates['coverage']['status']}")
    print(f"Freshness:       {gates['freshness']['status']}")
    print(f"Integrity:       {gates['integrity']['status']}")
    print(f"OI:              {gates['oi_consecutive_state']['status']}")
    print(f"Decision/Intel:  {gates['decision_intelligence']['status']}")
    print(f"Result:          {'PASS' if not blocking_failures else 'FAIL'}")
    print(f"Report:          {os.path.relpath(args.output, PROJECT_ROOT)}")
    print(f"Summary:         {os.path.relpath(args.summary_output, PROJECT_ROOT)}")

    if blocking_failures:
        print("LIVE_SESSION_VALIDATION=FAIL")
        return 2

    print("LIVE_SESSION_VALIDATION=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
