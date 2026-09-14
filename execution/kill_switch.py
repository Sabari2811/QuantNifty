from __future__ import annotations


class KillSwitch:
    """Explicit operator-controlled execution stop."""

    def __init__(self):
        self.active = False
        self.reason = ""

    def activate(self, reason: str = "Operator stop") -> None:
        self.active = True
        self.reason = reason

    def deactivate(self) -> None:
        self.active = False
        self.reason = ""

    def is_active(self) -> bool:
        return self.active
