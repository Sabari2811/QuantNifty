from __future__ import annotations

from dashboard.decision_adapter import adapt_decision
from dashboard.intelligence_adapter import adapt_intelligence
from dashboard.market_summary_adapter import adapt_market_summary
from dashboard.provenance_adapter import adapt_provenance


def _status(ok: bool) -> str:
    return "MATCH" if ok else "GAP"


def build_live_reconciliation(dashboard) -> dict:
    """Build a field-level reconciliation report from one DashboardData cycle.

    The report compares the values handed to the UI adapters with their
    authoritative DashboardData sources. It never recalculates analytics.
    """
    summary = adapt_market_summary(dashboard)
    decision = adapt_decision(dashboard)
    intelligence = dashboard.intelligence
    provenance = adapt_provenance(dashboard.data_provenance)

    option_chain = dashboard.option_chain
    greeks = dashboard.greeks

    option_chain_rows = 0 if option_chain is None else len(option_chain)
    greek_rows = 0 if greeks is None else len(greeks)

    option_chain_identity = False
    greek_identity = False
    identity_gap = None
    if option_chain is not None and greeks is not None:
        keys = ["Strike", "CE_ID", "PE_ID"]
        if all(key in option_chain.columns for key in keys) and all(
            key in greeks.columns for key in keys
        ):
            option_keys = set(map(tuple, option_chain[keys].itertuples(index=False, name=None)))
            greek_keys = set(map(tuple, greeks[keys].itertuples(index=False, name=None)))
            option_chain_identity = len(option_keys) == option_chain_rows
            greek_identity = len(greek_keys) == greek_rows
            missing_greek_keys = sorted(option_keys - greek_keys)
            extra_greek_keys = sorted(greek_keys - option_keys)
            if missing_greek_keys or extra_greek_keys:
                identity_gap = {
                    "missing_greek_contracts": missing_greek_keys,
                    "extra_greek_contracts": extra_greek_keys,
                }

    fields = {
        "market_summary": {
            "spot": {"backend": dashboard.spot, "ui": summary["spot"]},
            "atm_strike": {"backend": (dashboard.expected_move or {}).get("atm_strike"), "ui": summary["atm_strike"]},
            "expected_move": {"backend": (dashboard.expected_move or {}).get("expected_move"), "ui": summary["expected_move"]},
            "expected_move_lower": {"backend": (dashboard.expected_move or {}).get("lower"), "ui": summary["expected_move_lower"]},
            "expected_move_upper": {"backend": (dashboard.expected_move or {}).get("upper"), "ui": summary["expected_move_upper"]},
            "pcr": {"backend": (dashboard.pcr or {}).get("oi_pcr"), "ui": summary["pcr"]},
            "max_pain": {"backend": (dashboard.max_pain or {}).get("max_pain"), "ui": summary["max_pain"]},
            "expiry": {"backend": dashboard.expiry, "ui": summary["expiry"]},
        },
        "decision": {
            key: {"backend": value, "ui": decision[key]}
            for key, value in decision.items()
        },
        "intelligence": intelligence,
        "option_chain": {
            "backend_rows": option_chain_rows,
            "greek_rows": greek_rows,
            "contract_identity": {
                "option_chain_unique": option_chain_identity,
                "greeks_unique": greek_identity,
                "gap": identity_gap,
            },
        },
        "provenance": provenance,
    }

    field_gaps = []
    for section, values in fields["market_summary"].items():
        if values["backend"] != values["ui"]:
            field_gaps.append(f"market_summary.{section}")
    for key, values in fields["decision"].items():
        if values["backend"] != values["ui"]:
            field_gaps.append(f"decision.{key}")
    if identity_gap:
        field_gaps.append("option_chain.contract_identity")

    fields["field_status"] = _status(not field_gaps)
    fields["gaps"] = tuple(field_gaps)
    return fields
