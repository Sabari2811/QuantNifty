"""Build a single non-secret validation report from independent gates."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class CertificationReport:
    overall: str
    live_certification: str
    strategy_contract: str
    backtest_gate: str
    temporal_integrity: str
    walk_forward: str
    robustness: str
    notes: tuple[str, ...]


def _state(value: Any) -> str:
    if value is True:
        return "PASS"
    if value is False:
        return "FAIL"
    return str(value or "NOT_VERIFIED").upper()


def build_certification_report(
    *,
    live_certification: Any = None,
    strategy_contract: Any = None,
    backtest_gate: Any = None,
    temporal_integrity: Any = None,
    walk_forward: Any = None,
    robustness: Any = None,
    notes: tuple[str, ...] = (),
) -> CertificationReport:
    states = {
        "live_certification": _state(getattr(live_certification, "passed", live_certification)),
        "strategy_contract": _state(getattr(strategy_contract, "passed", strategy_contract)),
        "backtest_gate": _state(getattr(backtest_gate, "passed", backtest_gate)),
        "temporal_integrity": _state(temporal_integrity),
        "walk_forward": _state(walk_forward),
        "robustness": _state(robustness),
    }
    overall = "PASS" if all(value == "PASS" for value in states.values()) else "NOT_CERTIFIED"
    return CertificationReport(overall=overall, notes=tuple(notes), **states)


def certification_report_as_dict(report: CertificationReport) -> dict[str, Any]:
    """Return a secret-free JSON-compatible representation."""
    return asdict(report)
