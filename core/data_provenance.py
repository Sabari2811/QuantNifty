from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True, slots=True)
class AcquisitionProvenance:
    """Immutable provenance for one runtime market-data acquisition."""

    source: str
    acquired_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    provider_timestamp: datetime | None = None
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

    @classmethod
    def from_dict(cls, value: dict[str, Any] | None) -> "AcquisitionProvenance | None":
        if value is None:
            return None

        acquired_at = value.get("acquired_at")
        if isinstance(acquired_at, str):
            acquired_at = datetime.fromisoformat(
                acquired_at.replace("Z", "+00:00")
            )
        elif acquired_at is None:
            acquired_at = datetime.now(timezone.utc)

        provider_timestamp = value.get("provider_timestamp")
        if isinstance(provider_timestamp, str):
            provider_timestamp = datetime.fromisoformat(
                provider_timestamp.replace("Z", "+00:00")
            )
        elif provider_timestamp is not None and not isinstance(
            provider_timestamp, datetime
        ):
            provider_timestamp = None

        return cls(
            source=str(value.get("source", "")),
            acquired_at=acquired_at,
            provider_timestamp=provider_timestamp,
            expected_count=int(value.get("expected_count", 0)),
            received_count=int(value.get("received_count", 0)),
            missing_count=int(value.get("missing_count", 0)),
            freshness_verified=bool(value.get("freshness_verified", False)),
            freshness_seconds=(
                None
                if value.get("freshness_seconds") is None
                else float(value["freshness_seconds"])
            ),
            reasons=tuple(value.get("reasons", ())),
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

    @classmethod
    def from_dict(cls, value: dict[str, Any] | None) -> "RuntimeDataProvenance":
        if not value:
            return cls()
        return cls(
            option_chain=AcquisitionProvenance.from_dict(value.get("option_chain")),
            candles=AcquisitionProvenance.from_dict(value.get("candles")),
            spot=AcquisitionProvenance.from_dict(value.get("spot")),
        )
