from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any


def _get(obj: Any, path: str):
    current = obj
    for part in path.split("."):
        if isinstance(current, dict):
            current = current.get(part)
        else:
            current = getattr(current, part, None)
    return current


def _same(left: Any, right: Any) -> bool:
    if left is right:
        return True
    if hasattr(left, "equals") and hasattr(right, "equals"):
        try:
            return bool(left.equals(right))
        except Exception:
            pass
    if is_dataclass(left):
        left = asdict(left)
    if is_dataclass(right):
        right = asdict(right)
    try:
        result = left == right
        return bool(result) if not hasattr(result, "all") else bool(result.all())
    except Exception:
        return False


def _check(report, name: str, backend: Any, dashboard: Any, rule: str = "exact"):
    passed = _same(backend, dashboard)
    report["checks"].append({"field": name, "rule": rule, "status": "PASS" if passed else "MISMATCH", "backend": backend, "dashboard": dashboard})


def reconcile_dashboard_cycle(ctx, dashboard_data) -> dict:
    """Compare one canonical runtime context with its DashboardData projection."""
    report = {"checks": []}
    for field in ("symbol", "spot", "expiry", "trade_status", "trade_block_reason", "runtime_status", "cycle_no"):
        _check(report, field, _get(ctx, field), _get(dashboard_data, field))
    _check(report, "option_chain", ctx.option_chain, dashboard_data.option_chain, "same_object")
    _check(report, "greeks", ctx.greeks_df, dashboard_data.greeks, "same_object")
    _check(report, "data_provenance", ctx.data_provenance, dashboard_data.data_provenance)
    _check(report, "option_chain_integrity", ctx.option_chain.attrs.get("quote_integrity") if ctx.option_chain is not None else None, dashboard_data.option_chain_integrity)

    analytics = ctx.analytics or {}
    for key in ("dealer_flow", "expected_move", "max_pain", "pcr", "market_structure", "liquidity", "probability", "signal", "trade_plan", "risk", "institutional_score"):
        _check(report, f"analytics.{key}", analytics.get(key, {}), _get(dashboard_data, key))

    dealer = analytics.get("dealer", {})
    for key in ("dealer_gamma", "market_mode", "support", "resistance", "gamma_flip", "gamma_wall", "expected_volatility", "mean_reversion_probability", "breakout_probability", "total_gex"):
        _check(report, f"dealer.{key}", dealer.get(key), _get(dashboard_data, f"dealer.{key}"))

    canonical = getattr(ctx, "intelligence", None)
    adapted = getattr(dashboard_data, "intelligence", None)
    if canonical is None:
        _check(report, "intelligence", None, adapted, "explicit_none")
    else:
        for key in ("contract_version", "timestamp", "recommendation", "direction", "confidence_before", "confidence_after", "conviction", "opportunity_quality", "execution_quality", "risk_quality", "explanation", "regime", "primary_scenario", "alternative_scenario", "invalidation", "reasons", "evidence_summary", "evidence", "historical_evidence", "data_quality"):
            _check(report, f"intelligence.{key}", _get(canonical, key), adapted.get(key) if isinstance(adapted, dict) else None, "adapter_contract")

    report["passed"] = sum(c["status"] == "PASS" for c in report["checks"])
    report["mismatches"] = sum(c["status"] == "MISMATCH" for c in report["checks"])
    report["status"] = "PASS" if report["mismatches"] == 0 else "GAP"
    return report
