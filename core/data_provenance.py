from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True, slots=True)
class AcquisitionProvenance:
    """Immutable provenance for one runtime market-data acquisition."""

    source: str
    acquired_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    expected_count: int = 0
    received_count: int = 0
    missing_count: int = 0
    freshness_verified: bool = False
    freshness_seconds: float | None = None
    reasons: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.expected_count < 0:
            raise ValueError("expected_count cannot be negative")
        if self.received_count < 0:
            raise ValueError("received_count cannot be negative")
        if self.missing_count < 0:
            raise ValueError("missing_count cannot be negative")
        if self.received_count > self.expected_count:
            raise ValueError("received_count cannot exceed expected_count")
        if self.freshness_seconds is not None and self.freshness_seconds < 0:
            raise ValueError("freshness_seconds cannot be negative")

    @property
    def complete(self) -> bool:
        return (
            self.expected_count == self.received_count
            and self.missing_count == 0
        )


@dataclass(frozen=True, slots=True)
class RuntimeDataProvenance:
    """Immutable acquisition provenance carried through RuntimeContext."""

    option_chain: AcquisitionProvenance | None = None
    candles: AcquisitionProvenance | None = None
    spot: AcquisitionProvenance | None = None

    @property
    def complete(self) -> bool:
        acquisitions = (
            self.option_chain,
            self.candles,
            self.spot,
        )
        present = tuple(item for item in acquisitions if item is not None)
        return bool(present) and all(item.complete for item in present)
