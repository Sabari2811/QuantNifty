"""Deterministic alert evaluation over canonical dashboard/runtime state.

This module creates alert events only; delivery (Telegram, email, UI, etc.) is
an integration concern and is deliberately kept outside the decision engine.
"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AlertEvent:
    code: str
    severity: str
    message: str
    cycle_no: int = 0


class AlertEngine:
    """Evaluate explicit state transitions and runtime failures.

    The engine is fail-closed: absent or invalid fields do not create trading
    alerts. It also keeps alert generation separate from actionability.
    """

    def evaluate(self, dashboard: Any, previous: Any = None) -> list[AlertEvent]:
        events: list[AlertEvent] = []
        cycle_no = int(getattr(dashboard, "cycle_no", 0) or 0)

        runtime_status = str(getattr(dashboard, "runtime_status", "") or "").upper()
        if runtime_status in {"FAILED", "ERROR", "UNAVAILABLE"}:
            events.append(AlertEvent("RUNTIME_FAILURE", "CRITICAL", runtime_status, cycle_no))

        decision = getattr(dashboard, "signal", None)
        if isinstance(decision, dict):
            invalidated = decision.get("invalidated") is True
            if invalidated:
                events.append(AlertEvent("DECISION_INVALIDATION", "HIGH", "Decision invalidated", cycle_no))

            confidence = decision.get("confidence")
            if isinstance(confidence, (int, float)) and not isinstance(confidence, bool):
                if confidence >= 80:
                    events.append(AlertEvent("HIGH_CONVICTION", "HIGH", f"Confidence {confidence}", cycle_no))

        dealer = getattr(dashboard, "dealer", None)
        if isinstance(dealer, dict):
            previous_dealer = previous.get("dealer") if isinstance(previous, dict) else None
            current_gamma = dealer.get("dealer_gamma") or dealer.get("gamma_regime")
            previous_gamma = previous_dealer.get("dealer_gamma") if isinstance(previous_dealer, dict) else None
            if current_gamma and previous_gamma and current_gamma != previous_gamma:
                events.append(
                    AlertEvent(
                        "GAMMA_REGIME_TRANSITION",
                        "HIGH",
                        f"{previous_gamma} -> {current_gamma}",
                        cycle_no,
                    )
                )

        return events
