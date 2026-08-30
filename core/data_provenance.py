from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True, slots=True)
class AcquisitionProvenance:
    """Immutable provenance for one runtime market-data acquisition."""

    source: str
    acquired_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expected_count: int = 0
    received_count: int = 0
    missing_count: int = 0
    freshness_verified: bool = False
    freshness_seconds: float | None = None
    reasons: tuple[str, ...] = ()
    provider_timestamp: datetime | None = None
    integrity_status: str = "UNVERIFIED"
    integrity_reasons: tuple[str, ...] = ()
    freshness_status_override: str | None = None

    def __post_init__(self) -> None:
        if self.expected_count < 0 or self.received_count < 0 or self.missing_count < 0:
            raise ValueError("provenance counts cannot be negative")
        if self.received_count > self.expected_count:
            raise ValueError("received_count cannot exceed expected_count")
        if self.freshness_seconds is not None and self.freshness_seconds < 0:
            raise ValueError("freshness_seconds cannot be negative")
        if self.integrity_status not in {"UNVERIFIED", "VALID", "SUSPECT", "INVALID"}:
            raise ValueError("invalid integrity_status")
        if self.freshness_status_override not in {None, "UNVERIFIED", "FRESH", "AGING", "STALE"}:
            raise ValueError("invalid freshness_status_override")

    @property
    def complete(self) -> bool:
        return self.expected_count == self.received_count and self.missing_count == 0

    @property
    def coverage_ratio(self) -> float:
        if self.expected_count <= 0:
            return 0.0
        return min(100.0, max(0.0, (self.received_count / self.expected_count) * 100.0))

    @property
    def coverage_status(self) -> str:
        if self.expected_count <= 0:
            return "UNVERIFIED"
        if self.complete:
            return "COMPLETE"
        if self.received_count == 0:
            return "EMPTY"
        return "PARTIAL"

    @property
    def freshness_status(self) -> str:
        if self.freshness_status_override is not None:
            return self.freshness_status_override
        return "VERIFIED" if self.freshness_verified else "UNVERIFIED"

    @property
    def status(self) -> str:
        if self.integrity_status == "INVALID":
            return "INVALID"
        if self.integrity_status == "SUSPECT":
            return "SUSPECT"
        if self.coverage_status == "EMPTY":
            return "EMPTY"
        if self.coverage_status == "PARTIAL":
            return "PARTIAL"
        if self.freshness_status in {"UNVERIFIED", "STALE"}:
            return "FRESHNESS_UNVERIFIED" if self.freshness_status == "UNVERIFIED" else "STALE"
        return "VALID"

    def as_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value.update({
            "coverage_ratio": self.coverage_ratio,
            "coverage_status": self.coverage_status,
            "freshness_status": self.freshness_status,
            "status": self.status,
        })
        return value

    @classmethod
    def from_dict(cls, value: dict[str, Any] | None) -> "AcquisitionProvenance | None":
        if value is None:
            return None
        acquired_at = value.get("acquired_at")
        if isinstance(acquired_at, str):
            acquired_at = datetime.fromisoformat(acquired_at.replace("Z", "+00:00"))
        elif acquired_at is None:
            acquired_at = datetime.now(timezone.utc)
        provider_timestamp = value.get("provider_timestamp")
        if isinstance(provider_timestamp, str):
            provider_timestamp = datetime.fromisoformat(provider_timestamp.replace("Z", "+00:00"))
        elif provider_timestamp is not None and not isinstance(provider_timestamp, datetime):
            provider_timestamp = None
        return cls(
            source=str(value.get("source", "")),
            acquired_at=acquired_at,
            expected_count=int(value.get("expected_count", 0)),
            received_count=int(value.get("received_count", 0)),
            missing_count=int(value.get("missing_count", 0)),
            freshness_verified=bool(value.get("freshness_verified", False)),
            freshness_seconds=None if value.get("freshness_seconds") is None else float(value["freshness_seconds"]),
            reasons=tuple(value.get("reasons", ())),
            provider_timestamp=provider_timestamp,
            integrity_status=str(value.get("integrity_status", "UNVERIFIED")),
            integrity_reasons=tuple(value.get("integrity_reasons", ())),
            freshness_status_override=value.get("freshness_status_override"),
        )


@dataclass(frozen=True, slots=True)
class RuntimeDataProvenance:
    option_chain: AcquisitionProvenance | None = None
    candles: AcquisitionProvenance | None = None
    spot: AcquisitionProvenance | None = None

    @property
    def complete(self) -> bool:
        acquisitions = tuple(item for item in (self.option_chain, self.candles, self.spot) if item is not None)
        return bool(acquisitions) and all(item.complete for item in acquisitions)

    @property
    def coverage_ratio(self) -> float:
        acquisitions = tuple(item for item in (self.option_chain, self.candles, self.spot) if item is not None and item.expected_count > 0)
        if not acquisitions:
            return 0.0
        expected = sum(item.expected_count for item in acquisitions)
        received = sum(item.received_count for item in acquisitions)
        return min(100.0, max(0.0, (received / expected) * 100.0))

    def as_dict(self) -> dict[str, Any]:
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
