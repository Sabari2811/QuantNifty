from __future__ import annotations

from dataclasses import dataclass


@dataclass
class KillSwitch:
    """Explicit runtime execution stop that fails closed when enabled."""

    enabled: bool = False
    reason: str = ""

    def activate(self, reason: str) -> None:
        normalized = reason.strip()
        if not normalized:
            raise ValueError("Kill switch activation reason is required")
        self.enabled = True
        self.reason = normalized

    def deactivate(self) -> None:
        self.enabled = False
        self.reason = ""

    def check(self) -> tuple[bool, str]:
        if self.enabled:
            return False, self.reason or "Kill switch is active."
        return True, "Kill switch is inactive."
