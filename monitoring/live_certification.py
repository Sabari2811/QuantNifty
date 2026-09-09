"""Fail-closed verification for captured live validation evidence.

This module evaluates persisted cycle evidence only. It never creates live
market evidence and never treats deployment or configuration as certification.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Iterable


@dataclass(frozen=True)
class LiveCertificationResult:
    passed: bool
    cycles_checked: int
    valid_live_cycles: int
    reasons: tuple[str, ...]


def _finite_number(value: Any) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def certify_live_session(
    records: Iterable[Any],
    *,
    min_cycles: int = 3,
) -> LiveCertificationResult:
    """Verify a captured session against the minimum live-certification gates.

    Every cycle must prove live identity, usable spot data, complete/valid
    option-chain state, fresh provenance, and durable database persistence.
    Missing or malformed evidence fails closed.
    """
    rows = list(records)
    reasons: list[str] = []
    if min_cycles < 1:
        raise ValueError("min_cycles must be >= 1")
    if len(rows) < min_cycles:
        reasons.append(f"insufficient_cycles:{len(rows)}<{min_cycles}")

    valid_live_cycles = 0
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            reasons.append(f"cycle_{index}:malformed_record")
            continue

        failures: list[str] = []
        if str(row.get("evidence_state", "")).upper() != "VALID_LIVE":
            failures.append("evidence_not_valid_live")
        if str(row.get("provider_mode", "")).upper() != "LIVE_PROVIDER":
            failures.append("provider_mode_not_live")
        if str(row.get("provider", "")).upper() not in {"INDMONEY", "INDSTOCKS", "INDSTOCKS_PROVIDER"}:
            failures.append("unsupported_provider")
        if not _finite_number(row.get("spot")):
            failures.append("spot_missing_or_invalid")
        if str(row.get("option_chain_coverage", "")).upper() != "COMPLETE":
            failures.append("option_chain_not_complete")
        if str(row.get("option_chain_integrity", "")).upper() != "VALID":
            failures.append("option_chain_not_valid")
        if str(row.get("provenance_freshness", "")).upper() != "FRESH":
            failures.append("provenance_not_fresh")
        if str(row.get("persistence_status", "")).upper() != "DURABLE_DATABASE":
            failures.append("persistence_not_durable")

        if failures:
            reasons.extend(f"cycle_{index}:{failure}" for failure in failures)
        else:
            valid_live_cycles += 1

    passed = len(rows) >= min_cycles and valid_live_cycles >= min_cycles and not reasons
    return LiveCertificationResult(
        passed=passed,
        cycles_checked=len(rows),
        valid_live_cycles=valid_live_cycles,
        reasons=tuple(reasons),
    )
