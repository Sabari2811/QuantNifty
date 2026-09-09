"""Fail-closed temporal leakage checks for replay/backtest datasets."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable


def _parse(value: Any, label: str) -> datetime:
    if value is None:
        raise ValueError(f"{label}_missing")
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        raise ValueError(f"{label}_invalid") from None


def validate_no_future_information(
    records: Iterable[Any],
    *,
    decision_field: str = "decision_timestamp",
    feature_field: str = "feature_timestamp",
    outcome_field: str | None = "outcome_timestamp",
) -> tuple[bool, tuple[str, ...]]:
    """Ensure features are available no later than the decision and outcomes are later."""
    reasons: list[str] = []
    for index, row in enumerate(records, start=1):
        if not isinstance(row, dict):
            reasons.append(f"row_{index}:malformed_record")
            continue
        try:
            decision = _parse(row.get(decision_field), decision_field)
            feature = _parse(row.get(feature_field), feature_field)
        except ValueError as exc:
            reasons.append(f"row_{index}:{exc}")
            continue
        if feature > decision:
            reasons.append(f"row_{index}:future_feature")
        if outcome_field:
            raw_outcome = row.get(outcome_field)
            if raw_outcome is not None:
                try:
                    outcome = _parse(raw_outcome, outcome_field)
                    if outcome <= decision:
                        reasons.append(f"row_{index}:outcome_not_after_decision")
                except ValueError as exc:
                    reasons.append(f"row_{index}:{exc}")
    return not reasons, tuple(reasons)
