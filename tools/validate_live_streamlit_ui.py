"""Run the real Streamlit entrypoint and reconcile its same-cycle UI boundary.

This validator requires a live INDMoney session. It uses Streamlit AppTest so
it exercises the actual ``dashboard/app.py`` entrypoint instead of a detached
adapter-only test. The app exposes the exact DashboardData cycle and UI
arguments through audit-only session state; no presentation scraping is used.
"""

from __future__ import annotations

import argparse
import json

import pandas as pd
from streamlit.testing.v1 import AppTest

from dashboard.decision_adapter import adapt_decision
from dashboard.live_provider_reconciliation import compare_dashboard_ui_runtime
from dashboard.live_reconciliation import build_live_reconciliation


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", default="NIFTY")
    parser.add_argument("--levels", type=int, default=5)
    args = parser.parse_args()

    # AppTest initially has no rendered elements. Run once to construct the
    # sidebar controls, then set the requested values and rerun for the live
    # validation cycle.
    app = AppTest.from_file("dashboard/app.py")
    app.run(timeout=120)

    if app.exception:
        print("STREAMLIT_RUNTIME=FAIL")
        for exc in app.exception:
            print(str(exc))
        return 2

    if len(app.selectbox) == 0 or len(app.slider) == 0:
        print("STREAMLIT_RUNTIME=FAIL")
        print(
            "Expected sidebar controls were not rendered: "
            f"selectboxes={len(app.selectbox)}, sliders={len(app.slider)}"
        )
        return 2

    app.selectbox[0].set_value(args.symbol)
    app.slider[0].set_value(args.levels)
    app.run(timeout=120)

    if app.exception:
        print("STREAMLIT_RUNTIME=FAIL")
        for exc in app.exception:
            print(str(exc))
        return 2

    state = app.session_state
    if "_quantnifty_dashboard_audit" not in state:
        print("STREAMLIT_RUNTIME=FAIL")
        print("Missing _quantnifty_dashboard_audit session state")
        return 2
    if "_quantnifty_ui_contract" not in state:
        print("STREAMLIT_RUNTIME=FAIL")
        print("Missing _quantnifty_ui_contract session state")
        return 2

    dashboard = state["_quantnifty_dashboard_audit"]
    contract = state["_quantnifty_ui_contract"]

    expected_decision = adapt_decision(dashboard)
    decision_ok = contract["decision"] == expected_decision
    intelligence_ok = contract["intelligence"] is dashboard.intelligence
    consistency_ok = (
        contract["decision_intelligence_consistency"]
        is dashboard.decision_intelligence_consistency
    )
    provenance_ok = contract["provenance"] is dashboard.data_provenance
    integrity_ok = contract["option_chain_integrity"] is dashboard.option_chain_integrity

    try:
        pd.testing.assert_frame_equal(contract["option_chain"], dashboard.option_chain)
        option_chain_ok = True
    except AssertionError:
        option_chain_ok = False

    try:
        pd.testing.assert_frame_equal(contract["greeks"], dashboard.greeks)
        greeks_ok = True
    except AssertionError:
        greeks_ok = False

    ui_contract_ok = all(
        [
            decision_ok,
            intelligence_ok,
            consistency_ok,
            provenance_ok,
            integrity_ok,
            option_chain_ok,
            greeks_ok,
        ]
    )

    mapping_report = compare_dashboard_ui_runtime(dashboard)
    live_report = build_live_reconciliation(dashboard)

    result = {
        "symbol": dashboard.symbol,
        "cycle_no": dashboard.cycle_no,
        "runtime_status": dashboard.runtime_status,
        "ui_contract": {
            "status": "PASS" if ui_contract_ok else "GAP",
            "decision": decision_ok,
            "intelligence": intelligence_ok,
            "decision_intelligence_consistency": consistency_ok,
            "provenance": provenance_ok,
            "option_chain_integrity": integrity_ok,
            "option_chain": option_chain_ok,
            "greeks": greeks_ok,
        },
        "dashboard_ui_runtime": mapping_report,
        "live_reconciliation": live_report,
    }
    print(json.dumps(result, indent=2, default=str))

    gaps = []
    if not ui_contract_ok:
        gaps.append("streamlit_ui_contract")
    gaps.extend(mapping_report.get("gaps", []))
    gaps.extend(live_report.get("gaps", []))

    if gaps:
        print("STREAMLIT_UI_RECONCILIATION=GAP")
        for gap in dict.fromkeys(gaps):
            print(f"GAP: {gap}")
        return 2

    print("STREAMLIT_UI_RECONCILIATION=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
