from __future__ import annotations

from dashboard.components.option_chain import _merge_authoritative_greeks
from dashboard.decision_adapter import adapt_decision
from dashboard.intelligence_adapter import adapt_intelligence
from dashboard.market_summary_adapter import adapt_market_summary
from dashboard.provenance_adapter import adapt_provenance


def _status(ok: bool) -> str:
    return "MATCH" if ok else "GAP"


def _dataframe_values_equal(left, right) -> bool:
    if left is None or right is None:
        return left is right
    return bool(left.reset_index(drop=True).equals(right.reset_index(drop=True)))


def _decision_backend_values(dashboard) -> dict:
    # Use the same canonical adapter contract as the UI. The reconciliation
    # layer must validate the actual UI-facing mapping, not maintain a parallel
    # ownership rule that can drift from adapt_decision().
    return adapt_decision(dashboard)


def build_live_reconciliation(dashboard) -> dict:
    """Build a field-level reconciliation report from one DashboardData cycle.

    The report compares values handed to UI adapters/components with their
    authoritative DashboardData sources. It never recalculates analytics.
    """
    summary = adapt_market_summary(dashboard)
    decision = adapt_decision(dashboard)
    decision_backend = _decision_backend_values(dashboard)
    canonical_intelligence = getattr(dashboard, "canonical_intelligence", None)
    intelligence = dashboard.intelligence
    canonical_intelligence_ui = adapt_intelligence(canonical_intelligence)
    provenance = adapt_provenance(dashboard.data_provenance)

    option_chain = dashboard.option_chain
    greeks = dashboard.greeks
    option_chain_rows = 0 if option_chain is None else len(option_chain)
    greek_rows = 0 if greeks is None else len(greeks)

    identity_gap = None
    option_chain_identity = False
    greek_identity = False
    if option_chain is not None and greeks is not None:
        keys = ["Strike", "CE_ID", "PE_ID"]
        if all(key in option_chain.columns for key in keys) and all(key in greeks.columns for key in keys):
            option_keys = set(map(tuple, option_chain[keys].itertuples(index=False, name=None)))
            greek_keys = set(map(tuple, greeks[keys].itertuples(index=False, name=None)))
            option_chain_identity = len(option_keys) == option_chain_rows
            greek_identity = len(greek_keys) == greek_rows
            missing = sorted(option_keys - greek_keys)
            extra = sorted(greek_keys - option_keys)
            if missing or extra:
                identity_gap = {
                    "missing_greek_contracts": missing,
                    "extra_greek_contracts": extra,
                }

    option_projection = None
    option_projection_matches = False
    option_projection_gap = None
    if option_chain is not None:
        option_projection = _merge_authoritative_greeks(option_chain, greeks)
        if option_projection is None:
            option_projection_gap = "projection_unavailable"
        elif identity_gap:
            option_projection_gap = identity_gap
        elif len(option_projection) != option_chain_rows:
            option_projection_gap = {
                "canonical_rows": option_chain_rows,
                "projected_rows": len(option_projection),
            }
        else:
            source_columns = list(option_chain.columns)
            source_values_match = (
                source_columns == [column for column in option_projection.columns if column in source_columns]
                and _dataframe_values_equal(option_chain[source_columns], option_projection[source_columns])
            )
            greek_values_match = True
            if greeks is not None and not greeks.empty:
                greek_columns = [
                    column for column in greeks.columns
                    if column not in option_chain.columns
                ]
                missing_projection_columns = [
                    column for column in greek_columns
                    if column not in option_projection.columns
                ]
                if missing_projection_columns:
                    greek_values_match = False
                    option_projection_gap = {
                        "missing_projected_greek_columns": missing_projection_columns,
                    }
                elif greek_columns:
                    greek_values_match = _dataframe_values_equal(
                        greeks[greek_columns].reset_index(drop=True),
                        option_projection[greek_columns].reset_index(drop=True),
                    )
                    if not greek_values_match:
                        option_projection_gap = "ui_projection_value_mismatch"
            option_projection_matches = source_values_match and greek_values_match

    intelligence_matches = canonical_intelligence_ui == intelligence
    intelligence_gap = None if intelligence_matches else "ui_intelligence_value_mismatch"

    decision_intelligence = getattr(dashboard, "decision_intelligence_consistency", None)
    if decision_intelligence is None:
        decision_intelligence_gap = "dashboard_decision_intelligence_status_missing"
    else:
        decision_intelligence_gap = None

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
            key: {"backend": decision_backend[key], "ui": value}
            for key, value in decision.items()
        },
        "intelligence": {
            "status": _status(intelligence_matches),
            "backend": canonical_intelligence_ui,
            "ui": intelligence,
            "gap": intelligence_gap,
        },
        "decision_intelligence": {
            "status": "MATCH" if decision_intelligence is not None else "GAP",
            "value": decision_intelligence,
            "gap": decision_intelligence_gap,
        },
        "option_chain": {
            "backend_rows": option_chain_rows,
            "greek_rows": greek_rows,
            "contract_identity": {
                "option_chain_unique": option_chain_identity,
                "greeks_unique": greek_identity,
                "gap": identity_gap,
            },
            "ui_projection": {
                "status": _status(option_projection_matches),
                "rows": 0 if option_projection is None else len(option_projection),
                "gap": option_projection_gap,
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
    if not intelligence_matches:
        field_gaps.append("intelligence")
    if decision_intelligence_gap:
        field_gaps.append("decision_intelligence")
    if identity_gap:
        field_gaps.append("option_chain.contract_identity")
    if not option_projection_matches:
        field_gaps.append("option_chain.ui_projection")

    fields["field_status"] = _status(not field_gaps)
    fields["gaps"] = tuple(field_gaps)
    return fields
