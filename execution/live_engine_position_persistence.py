from __future__ import annotations

from execution.position_runtime_service import PositionRuntimeService
from execution.position_state import PositionState


class LiveEnginePositionPersistence:
    """Explicit adapter for persisting canonical paper positions from runtime."""

    def __init__(self, service: PositionRuntimeService):
        if service is None:
            raise ValueError("Position runtime service is required")
        self.service = service

    def persist(self, position) -> PositionState:
        return self.service.persist_paper_position(position)

    def persist_after_lifecycle(self, position, lifecycle_decision, *, closed_at=None) -> PositionState:
        return self.service.persist_after_lifecycle(
            position,
            lifecycle_decision,
            closed_at=closed_at,
        )
