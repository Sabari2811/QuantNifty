from __future__ import annotations

from math import isclose
from typing import Any


def _equal(left: Any, right: Any) -> bool:
    if left is None or right is None:
        return left is right
    try:
        return isclose(float(left), float(right), rel_tol=0.0, abs_tol=1e-9)
    except (TypeError, ValueError):
        return left == right


def _raw_chain(raw_quotes: dict, option_chain):
    if option_chain is None:
        return None, ["option_chain_missing"]
    required = ["Strike", "CE_ID", "PE_ID"]
    missing = [column for column in required if column not in option_chain.columns]
    if missing:
        return None, [f"canonical_missing:{column}" for column in missing]

    rows = []
    for _, row in option_chain.reset_index(drop=True).iterrows():
        ce = raw_quotes.get(f"NFO_{int(row['CE_ID'])}")
        pe = raw_quotes.get(f"NFO_{int(row['PE_ID'])}")
        if ce is None or pe is None:
            return None, [f"provider_contract_missing:{int(row['Strike'])}"]
        rows.append(
            {
                "Strike": row["Strike"],
                "CE_LTP": ce.get("live_price"),
                "CE_OI": ce.get("open_interest"),
                "CE_VOLUME": ce.get("volume"),
                "PE_LTP": pe.get("live_price"),
                "PE_OI": pe.get("open_interest"),
                "PE_VOLUME": pe.get("volume"),
            }
        )
    return rows, []


def reconcile_raw_quote_analytics(raw_quotes: dict, option_chain, spot: float, analytics: dict) -> dict:
    """Independently recompute quote-derived analytics from captured provider quotes.

    This intentionally does not call any AnalyticsPipeline engine. It validates
    PCR, ATM-straddle expected move, and the repository's simplified max-pain
    definition directly from provider quote fields.
    """
    rows, gaps = _raw_chain(raw_quotes, option_chain)
    if gaps:
        return {"status": "GAP", "checks": [], "gaps": gaps}
    if not rows:
        return {"status": "GAP", "checks": [], "gaps": ["raw_option_chain_empty"]}

    call_oi = sum(float(row["CE_OI"] or 0) for row in rows)
    put_oi = sum(float(row["PE_OI"] or 0) for row in rows)
    call_volume = sum(float(row["CE_VOLUME"] or 0) for row in rows)
    put_volume = sum(float(row["PE_VOLUME"] or 0) for row in rows)

    oi_pcr = round(put_oi / call_oi, 2) if call_oi > 0 else 0
    volume_pcr = round(put_volume / call_volume, 2) if call_volume > 0 else 0

    atm = min(rows, key=lambda row: abs(float(row["Strike"]) - float(spot)))
    expected_move = round(float(atm["CE_LTP"]) + float(atm["PE_LTP"]), 2)
    expected_upper = round(float(spot) + expected_move, 2)
    expected_lower = round(float(spot) - expected_move, 2)

    max_pain_row = max(rows, key=lambda row: float(row["CE_OI"] or 0) + float(row["PE_OI"] or 0))
    max_pain = max_pain_row["Strike"]
    max_pain_call_oi = int(max_pain_row["CE_OI"] or 0)
    max_pain_put_oi = int(max_pain_row["PE_OI"] or 0)
    max_pain_total_oi = max_pain_call_oi + max_pain_put_oi

    expected = {
        "pcr.oi_pcr": oi_pcr,
        "pcr.volume_pcr": volume_pcr,
        "pcr.call_oi": int(call_oi),
        "pcr.put_oi": int(put_oi),
        "pcr.call_volume": int(call_volume),
        "pcr.put_volume": int(put_volume),
        "expected_move.atm_strike": atm["Strike"],
        "expected_move.expected_move": expected_move,
        "expected_move.upper": expected_upper,
        "expected_move.lower": expected_lower,
        "expected_move.method": "ATM_STRADDLE",
        "max_pain.max_pain": max_pain,
        "max_pain.call_oi": max_pain_call_oi,
        "max_pain.put_oi": max_pain_put_oi,
        "max_pain.total_oi": max_pain_total_oi,
    }

    checks = []
    for path, expected_value in expected.items():
        section, field = path.split(".", 1)
        actual_value = (analytics.get(section) or {}).get(field)
        passed = _equal(expected_value, actual_value)
        checks.append({
            "field": path,
            "expected_from_raw_provider": expected_value,
            "canonical_analytics": actual_value,
            "status": "PASS" if passed else "MISMATCH",
        })

    mismatches = [item["field"] for item in checks if item["status"] != "PASS"]
    return {
        "status": "PASS" if not mismatches else "GAP",
        "checks": checks,
        "gaps": mismatches,
        "raw_contracts": len(raw_quotes),
        "canonical_rows": len(option_chain),
        "validated_fields": len(checks),
    }
