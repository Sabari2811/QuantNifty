from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


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
    # Kept last so existing positional construction remains compatible.
    provider_timestamp: datetime | None = None
    # Separate from freshness: integrity is about whether received values
    # are structurally/pricing-consistent, not whether they are fresh.
    integrity_status: str = "UNVERIFIED"
    integrity_reasons: tuple[str, ...] = ()

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
        if self.integrity_status not in {
            "UNVERIFIED",
            "VALID",
            "SUSPECT",
            "INVALID",
        }:
            raise ValueError(
                "integrity_status must be UNVERIFIED, VALID, SUSPECT, or INVALID"
            )

    @property
    def complete(self) -> bool:
        return (
            self.expected_count == self.received_count
            and self.missing_count == 0
        )

    @property
    def coverage_ratio(self) -> float:
        """Return received/expected coverage as a percentage in [0, 100]."""
        if self.expected_count <= 0:
            return 0.0
        return min(100.0, max(0.0, (self.received_count / self.expected_count) * 100.0))

    @property
    def coverage_status(self) -> str:
        """Return a deterministic coverage state independent of integrity/freshness."""
        if self.expected_count <= 0:
            return "UNVERIFIED"
        if self.missing_count == 0 and self.received_count == self.expected_count:
            return "COMPLETE"
        if self.received_count == 0:
            return "EMPTY"
        return "PARTIAL"

    @property
    def freshness_status(self) -> str:
        """Return freshness state without conflating it with data integrity."""
        if self.freshness_verified:
            return "VERIFIED"
        return "UNVERIFIED"

    @property
    def status(self) -> str:
        """Compact backend status used by reconciliation/UI adapters."""
        if self.integrity_status == "INVALID":
            return "INVALID"
        if self.integrity_status == "SUSPECT":
            return "SUSPECT"
        if self.coverage_status == "EMPTY":
            return "EMPTY"
        if self.coverage_status == "PARTIAL":
            return "PARTIAL"
        if self.freshness_status == "UNVERIFIED":
            return "FRESHNESS_UNVERIFIED"
        return "VALID"

    def as_dict(self) -> dict[str, Any]:
        """Serialize the canonical provenance fields for reconciliation."""
        value = asdict(self)
        value.update(
            {
                "coverage_ratio": self.coverage_ratio,
                "coverage_status": self.coverage_status,
                "freshness_status": self.freshness_status,
                "status": self.status,
            }
        )
        return value

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
            provider_timestamp=provider_timestamp,
            integrity_status=str(value.get("integrity_status", "UNVERIFIED")),
            integrity_reasons=tuple(value.get("integrity_reasons", ())),
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

    @property
    def coverage_ratio(self) -> float:
        """Aggregate coverage across all present acquisitions."""
        acquisitions = tuple(
            item for item in (self.option_chain, self.candles, self.spot)
            if item is not None and item.expected_count > 0
        )
        if not acquisitions:
            return 0.0
        expected = sum(item.expected_count for item in acquisitions)
        received = sum(item.received_count for item in acquisitions)
        return min(100.0, max(0.0, (received / expected) * 100.0))

    def as_dict(self) -> dict[str, Any]:
        """Serialize all provenance while preserving derived validation state."""
        return {
            "option_chain": None if self.option_chain is None else self.option_chain.as_dict(),
            "candles": None if self.candles is None else self.candles.as_dict(),
            "spot": None if self.spot is None else self.spot.as_dict(),
            "coverage_ratio": self.coverage_ratio,
            "complete": self.complete,
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any] | None) -> "RuntimeDataProvenance":
        if not value:
            return cls()
        return cls(
            option_chain=AcquisitionProvenance.from_dict(value.get("option_chain")),
            candles=AcquisitionProvenance.from_dict(value.get("candles")),
            spot=AcquisitionProvenance.from_dict(value.get("spot")),
        )
