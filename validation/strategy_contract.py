"""Fail-closed validation of recorded strategy decisions.

This contract validates outputs after the strategy has run. It never creates,
modifies, or promotes a trading decision.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable


@dataclass(frozen=True)
class StrategyContractResult:
    passed: bool
    trades_checked: int
    reasons: tuple[str, ...]


def _date_key(value: Any) -> str:
    if value is None:
        raise ValueError("timestamp_missing")
    text = str(value)
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        return text[:10]


def validate_strategy_records(
    records: Iterable[Any],
    *,
    max_trades_per_day: int | None = 3,
) -> StrategyContractResult:
    """Validate trade records against safety invariants used by after-market tests."""
    if max_trades_per_day is not None and max_trades_per_day < 1:
        raise ValueError("max_trades_per_day must be >= 1")

    rows = list(records)
    reasons: list[str] = []
    daily: dict[str, int] = {}
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            reasons.append(f"trade_{index}:malformed_record")
            continue
        actionability = row.get("actionable")
        risk_allowed = row.get("risk_allowed")
        execution = str(row.get("execution_status", "")).upper()
        if actionability is False and execution in {"EXECUTED", "SUBMITTED"}:
            reasons.append(f"trade_{index}:executed_while_not_actionable")
        if risk_allowed is False and execution in {"EXECUTED", "SUBMITTED"}:
            reasons.append(f"trade_{index}:executed_while_risk_blocked")
        if execution == "UNKNOWN" and row.get("reconciliation_required") is not True:
            reasons.append(f"trade_{index}:unknown_requires_reconciliation")
        if max_trades_per_day is not None:
            try:
                day = _date_key(row.get("timestamp"))
            except ValueError as exc:
                reasons.append(f"trade_{index}:{exc}")
                continue
            daily[day] = daily.get(day, 0) + 1
            if daily[day] > max_trades_per_day:
                reasons.append(f"trade_{index}:daily_trade_limit_exceeded:{daily[day]}>{max_trades_per_day}")

    return StrategyContractResult(not reasons, len(rows), tuple(reasons))
