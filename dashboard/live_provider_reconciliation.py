from __future__ import annotations

from math import isclose
from typing import Any

from analytics.intelligence.decision_consistency import reconcile_decision_intelligence


QUOTE_FIELDS = (
    ("CE_LTP", "live_price"),
    ("CE_OI", "open_interest"),
    ("CE_VOLUME", "volume"),
    ("PE_LTP", "live_price"),
    ("PE_OI", "open_interest"),
    ("PE_VOLUME", "volume"),
)


def _equal(left: Any, right: Any) -> bool:
    if left is None or right is None:
        return left is right
    try:
        lf = float(left)
        rf = float(right)
        return isclose(lf, rf, rel_tol=0.0, abs_tol=1e-9)
    except (TypeError, ValueError):
        return left == right


def compare_raw_quotes_to_option_chain(raw_quotes: dict, option_chain) -> dict:
    """Compare provider quote fields with every canonical option-chain row."""
    checks = []
    gaps = []
    if option_chain is None:
        return {"status": "GAP", "checks": [], "gaps": ["option_chain_missing"]}

    required = ["Strike", "CE_ID", "PE_ID"] + [field for field, _ in QUOTE_FIELDS]
    missing_columns = [column for column in required if column not in option_chain.columns]
    if missing_columns:
        return {
            "status": "GAP",
            "checks": [],
            "gaps": [f"canonical_missing:{column}" for column in missing_columns],
        }

    for row_no, row in option_chain.reset_index(drop=True).iterrows():
        for side, id_column in (("CE", "CE_ID"), ("PE", "PE_ID")):
            security_id = row[id_column]
            key = f"NFO_{int(security_id)}"
            quote = raw_quotes.get(key)
            for canonical_column, provider_column in (
                (f"{side}_LTP", "live_price"),
                (f"{side}_OI", "open_interest"),
                (f"{side}_VOLUME", "volume"),
            ):
                provider_value = None if quote is None else quote.get(provider_column)
                canonical_value = row[canonical_column]
                passed = _equal(canonical_value, provider_value)
                checks.append({
                    "row": int(row_no),
                    "security_id": int(security_id),
                    "field": canonical_column,
                    "status": "PASS" if passed else "MISMATCH",
                    "provider": provider_value,
                    "canonical": canonical_value,
                })
                if not passed:
                    gaps.append(f"row{row_no}.{canonical_column}:NFO_{int(security_id)}")

    return {
        "status": "PASS" if not gaps else "GAP",
        "checks": checks,
        "gaps": gaps,
        "rows": len(option_chain),
        "provider_contracts": len(raw_quotes),
    }


def _consistency_payload(result) -> dict:
    return {
        "status": result.status,
        "semantic_status": result.semantic_status,
        "consistent": result.consistent,
        "actionable": result.actionable,
        "vetoed": result.vetoed,
        "decision_signal": result.decision_signal,
        "intelligence_recommendation": result.intelligence_recommendation,
        "intelligence_direction": result.intelligence_direction,
        "reason": result.reason,
    }


def compare_decision_intelligence_runtime(ctx) -> dict:
    """Validate the semantic Decision ↔ Intelligence contract for one live cycle.

    Prefer the consistency result captured immediately after Decision and
    Intelligence synthesis, before the execution pipeline can mutate an
    invalid/unexecutable Decision signal to WAIT. This preserves the
    authoritative pre-execution decision semantics for runtime audit output.
    """
    stored = getattr(ctx, "decision_intelligence_consistency", None)
    if stored is not None:
        return _consistency_payload(stored)

    decision = getattr(ctx, "decision", None)
    intelligence = getattr(ctx, "intelligence", None)
    if decision is None or intelligence is None:
        return {
            "status": "GAP",
            "semantic_status": "UNAVAILABLE",
            "reason": "decision_or_intelligence_missing",
        }

    result = reconcile_decision_intelligence(decision, intelligence)
    return _consistency_payload(result)


def build_raw_provider_reconciliation(raw_quotes: dict, ctx) -> dict:
    """Build one audit report for provider→canonical data and decision semantics."""
    option_report = compare_raw_quotes_to_option_chain(raw_quotes, ctx.option_chain)
    decision_report = compare_decision_intelligence_runtime(ctx)
    gaps = []
    if option_report["status"] != "PASS":
        gaps.append("provider_to_option_chain")
    if decision_report["status"] != "CONSISTENT":
        gaps.append("decision_intelligence")
    return {
        "option_chain": option_report,
        "decision_intelligence": decision_report,
        "status": "PASS" if not gaps else "GAP",
        "gaps": gaps,
    }
