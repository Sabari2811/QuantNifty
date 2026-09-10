from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from dashboard.decision_adapter import adapt_decision
from dashboard.market_summary_adapter import adapt_market_summary


def _plain(value: Any) -> Any:
    """Convert UI-bound dataclasses/enums to stable, JSON-friendly values."""
    if is_dataclass(value):
        return _plain(asdict(value))
    if isinstance(value, dict):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    if hasattr(value, "value") and not isinstance(value, (str, bytes)):
        return _plain(value.value)
    return value


def build_ui_data_contract(dashboard) -> dict[str, Any]:
    """Build the exhaustive backend -> UI boundary contract for one cycle.

    Every section is sourced from DashboardData or the same canonical adapter
    used by the Streamlit entrypoint. No analytics, probabilities, prices, or
    trade values are recomputed here. The contract is intentionally explicit so
    a missing UI mapping becomes testable rather than remaining implicit.
    """
    decision = adapt_decision(dashboard)
    summary = adapt_market_summary(dashboard)
    trade_plan = dashboard.trade_plan or {}
    probability = dashboard.probability or {}
    dealer = dashboard.dealer
    risk = dashboard.risk or {}
    market_structure = dashboard.market_structure or {}
    dealer_flow = dashboard.dealer_flow or {}
    liquidity = dashboard.liquidity or {}
    max_pain = dashboard.max_pain or {}
    pcr = dashboard.pcr or {}

    return {
        "identity": {
            "provider": dashboard.provider,
            "symbol": dashboard.symbol,
            "spot": dashboard.spot,
            "expiry": dashboard.expiry,
        },
        "market_summary": summary,
        "market_banner": {
            "signal": decision.get("signal"),
            "spot": dashboard.spot,
            "dealer_gamma": dealer.dealer_gamma,
            "market_mode": dealer.market_mode,
            "gamma_flip": dealer.gamma_flip,
            "gamma_wall": dealer.gamma_wall,
            "bullish_probability": decision.get("bullish_probability"),
            "confidence": decision.get("confidence"),
            "recommended_strike": trade_plan.get("recommended_strike"),
            "option_type": trade_plan.get("option_type"),
            "risk_reward": trade_plan.get("risk_reward"),
        },
        "market_regime": {
            "dealer_gamma": dealer.dealer_gamma,
            "market_mode": dealer.market_mode,
            "expected_volatility": dealer.expected_volatility,
            "confidence": probability.get("confidence"),
            "bullish_probability": probability.get("bullish_probability"),
            "bearish_probability": probability.get("bearish_probability"),
            "mean_reversion_probability": dealer.mean_reversion_probability,
            "breakout_probability": dealer.breakout_probability,
            "gamma_flip": dealer.gamma_flip,
            "gamma_wall": dealer.gamma_wall,
            "total_gex": dealer.total_gex,
        },
        "decision": decision,
        "intelligence": dashboard.intelligence,
        "decision_intelligence_consistency": dashboard.decision_intelligence_consistency,
        "expected_move": dashboard.expected_move,
        "max_pain": max_pain,
        "pcr": pcr,
        "market_structure": market_structure,
        "dealer": {
            "dealer_gamma": dealer.dealer_gamma,
            "market_mode": dealer.market_mode,
            "support": dealer.support,
            "resistance": dealer.resistance,
            "gamma_flip": dealer.gamma_flip,
            "gamma_wall": dealer.gamma_wall,
            "expected_volatility": dealer.expected_volatility,
            "mean_reversion_probability": dealer.mean_reversion_probability,
            "breakout_probability": dealer.breakout_probability,
            "total_gex": dealer.total_gex,
        },
        "dealer_flow": dealer_flow,
        "liquidity": liquidity,
        "trade_plan": trade_plan,
        "risk": risk,
        "institutional_score": dashboard.institutional_score,
        "option_chain": dashboard.option_chain,
        "greeks": dashboard.greeks,
        "provenance": dashboard.data_provenance,
        "option_chain_integrity": dashboard.option_chain_integrity,
        "execution": {
            "intent": dashboard.execution_intent,
            "result": dashboard.execution_result,
            "lifecycle": dashboard.execution_lifecycle,
        },
        "position_state": {
            "position": dashboard.position,
            "last_trade": dashboard.last_trade,
            "portfolio": dashboard.portfolio,
            "recovery": dashboard.position_recovery,
            "reconciliation": dashboard.position_reconciliation,
        },
        "runtime": {
            "status": dashboard.runtime_status,
            "cycle_no": dashboard.cycle_no,
            "trade_status": dashboard.trade_status,
            "trade_block_reason": dashboard.trade_block_reason,
            "risk_state": dashboard.risk_state,
        },
        "brain": {
            "observation": dashboard.brain_observation,
            "persisted": bool(getattr(dashboard.brain_observation, "persisted", False)),
            "status": getattr(dashboard.brain_observation, "status", None),
            "cycle_no": getattr(dashboard.brain_observation, "cycle_no", None),
            "signal": getattr(dashboard.brain_observation, "signal", None),
            "outcome": getattr(dashboard.brain_observation, "outcome", None),
        },
        "paper_performance": {
            "journal": dashboard.journal,
            "statistics": dashboard.statistics,
        },
        "alignment": {
            "decision_vs_trade_plan_signal": decision.get("signal") == trade_plan.get("signal"),
            "decision_vs_trade_plan_signal_value": trade_plan.get("signal"),
            "decision_signal_value": decision.get("signal"),
        },
    }


def validate_ui_data_contract(contract: dict[str, Any]) -> list[str]:
    """Return deterministic mapping/integrity violations; empty means PASS."""
    errors: list[str] = []

    identity = contract.get("identity", {})
    summary = contract.get("market_summary", {})
    banner = contract.get("market_banner", {})
    decision = contract.get("decision", {})
    regime = contract.get("market_regime", {})
    trade_plan = contract.get("trade_plan", {})
    risk = contract.get("risk", {})
    brain = contract.get("brain", {})
    alignment = contract.get("alignment", {})

    if summary.get("spot") != identity.get("spot"):
        errors.append("market_summary.spot != identity.spot")
    if banner.get("spot") != identity.get("spot"):
        errors.append("market_banner.spot != identity.spot")
    if banner.get("signal") != decision.get("signal"):
        errors.append("market_banner.signal != decision.signal")
    if regime.get("bullish_probability") != decision.get("bullish_probability"):
        errors.append("market_regime.bullish_probability != decision.bullish_probability")
    if regime.get("confidence") != decision.get("confidence"):
        errors.append("market_regime.confidence != decision.confidence")
    if not alignment.get("decision_vs_trade_plan_signal"):
        errors.append("decision.signal != trade_plan.signal")
    if not risk:
        errors.append("risk policy/state is missing from the UI contract")

    if decision.get("signal") == "WAIT":
        if trade_plan.get("recommended_strike") not in (None, "", "-"):
            errors.append("WAIT decision has an active recommended strike")
        if not brain.get("persisted"):
            errors.append("WAIT decision has no persisted Brain observation")

    return errors


def build_ui_integrity_report(dashboard) -> dict[str, Any]:
    contract = build_ui_data_contract(dashboard)
    errors = validate_ui_data_contract(contract)
    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "contract": contract,
    }
