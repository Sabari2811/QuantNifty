from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from threading import Lock
from typing import Any


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
    """Guard that prevents client-order reuse across the process and restarts."""

    def __init__(self, audit_store: Any | None = None) -> None:
        self._seen: set[str] = set()
        self._lock = Lock()
        self._audit_store = audit_store

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

            # The durable audit store is the source of truth across process
            # restarts.  Any existing event means this client identity has
            # already participated in execution and must never be reused.
            if self._audit_store is not None and self._audit_store.get(key) is not None:
                self._seen.add(key)
                return IdempotencyDecision(
                    IdempotencyStatus.DUPLICATE,
                    key,
                    "Client order already exists in execution audit",
                )

            self._seen.add(key)

        return IdempotencyDecision(IdempotencyStatus.NEW, key)

    def contains(self, client_order_id: str) -> bool:
        return str(client_order_id).strip() in self._seen
