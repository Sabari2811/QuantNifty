from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from threading import Lock


class IdempotencyStatus(str, Enum):
    NEW = "NEW"
    DUPLICATE = "DUPLICATE"
    INVALID = "INVALID"


@dataclass(frozen=True, slots=True)
class IdempotencyDecision:
    status: IdempotencyStatus
    client_order_id: str
    reason: str = ""


class OrderIdempotencyGuard:
    """Process-local guard that prevents a client order identity from being submitted twice."""

    def __init__(self) -> None:
        self._seen: set[str] = set()
        self._lock = Lock()

    def check_and_reserve(self, client_order_id: str) -> IdempotencyDecision:
        key = str(client_order_id).strip()
        if not key:
            return IdempotencyDecision(
                IdempotencyStatus.INVALID,
                "",
                "client_order_id is required",
            )

        with self._lock:
            if key in self._seen:
                return IdempotencyDecision(
                    IdempotencyStatus.DUPLICATE,
                    key,
                    "Client order already reserved",
                )
            self._seen.add(key)

        return IdempotencyDecision(IdempotencyStatus.NEW, key)

    def contains(self, client_order_id: str) -> bool:
        return str(client_order_id).strip() in self._seen
