from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

from analytics.intelligence.evidence.models import HistoricalEvidence
from analytics.intelligence.models import TradeIntelligenceRecord


Direction = Literal[
    "BULLISH",
    "BEARISH",
    "NEUTRAL",
]

Decision = Literal[
    "BUY",
    "SELL",
    "WAIT",
    "NO_TRADE",
]

Regime = Literal[
    "TRENDING_UP",
    "TRENDING_DOWN",
    "RANGE",
    "BREAKOUT",
    "BREAKDOWN",
    "TRANSITION",
    "HIGH_VOLATILITY",
    "LOW_VOLATILITY",
    "UNKNOWN",
]


@dataclass(frozen=True, slots=True)
class EvidenceItem:
    """One normalized piece of decision evidence."""

    source_family: str
    feature: str

    direction: Direction = "NEUTRAL"

    strength: float = 0.0
    confidence: float = 0.0
    freshness: float = 100.0
    independence: float = 1.0

    reason: str = ""

    def __post_init__(self) -> None:

        for name in (
            "strength",
            "confidence",
            "freshness",
        ):
            value = getattr(self, name)

            if not 0.0 <= value <= 100.0:
                raise ValueError(
                    f"{name} must be between 0 and 100"
                )

        if not 0.0 <= self.independence <= 1.0:
            raise ValueError(
                "independence must be between 0 and 1"
            )

        if not self.source_family.strip():
            raise ValueError(
                "source_family must not be empty"
            )

        if not self.feature.strip():
            raise ValueError(
                "feature must not be empty"
            )


@dataclass(frozen=True, slots=True)
class EvidenceSummary:
    """Aggregate evidence without double-counting correlated signals."""

    bullish_count: int = 0
    bearish_count: int = 0
    neutral_count: int = 0

    independent_count: int = 0
    correlated_count: int = 0

    confluence_score: float = 0.0
    conflict_score: float = 0.0

    def __post_init__(self) -> None:

        for name in (
            "bullish_count",
            "bearish_count",
            "neutral_count",
            "independent_count",
            "correlated_count",
        ):
            if getattr(self, name) < 0:
                raise ValueError(
                    f"{name} cannot be negative"
                )

        for name in (
            "confluence_score",
            "conflict_score",
        ):
            value = getattr(self, name)

            if not 0.0 <= value <= 100.0:
                raise ValueError(
                    f"{name} must be between 0 and 100"
                )


@dataclass(frozen=True, slots=True)
class RegimeState:
    """Current market regime and transition information."""

    regime: Regime = "UNKNOWN"

    previous_regime: Regime = "UNKNOWN"

    transition: bool = False

    transition_reason: str = ""

    confidence: float = 0.0

    def __post_init__(self) -> None:

        if not 0.0 <= self.confidence <= 100.0:
            raise ValueError(
                "regime confidence must be between 0 and 100"
            )


@dataclass(frozen=True, slots=True)
class Scenario:
    """One plausible market scenario."""

    name: str

    direction: Direction = "NEUTRAL"

    probability: float = 0.0

    trigger: str = ""

    invalidation: str = ""

    rationale: str = ""

    def __post_init__(self) -> None:

        if not self.name.strip():
            raise ValueError(
                "scenario name must not be empty"
            )

        if not 0.0 <= self.probability <= 100.0:
            raise ValueError(
                "probability must be between 0 and 100"
            )


@dataclass(frozen=True, slots=True)
class DataQuality:
    """Quality gate for data used by Intelligence."""

    score: float = 100.0

    stale: bool = False

    incomplete: bool = False

    invalid: bool = False

    # True only when acquisition freshness was explicitly verified.
    # False means freshness is unverified, not that the data is stale.
    freshness_verified: bool = False

    reasons: tuple[str, ...] = field(
        default_factory=tuple
    )

    def __post_init__(self) -> None:

        if not 0.0 <= self.score <= 100.0:
            raise ValueError(
                "data quality score must be between 0 and 100"
            )


@dataclass(frozen=True, slots=True)
class IntelligenceResult:
    """
    Canonical R2-005 Intelligence result.

    Contains the current market fingerprint, historical evidence,
    synthesized decision evidence, regime, scenarios, quality gates,
    and final intelligence metrics.
    """

    # ==========================================================
    # Existing application contract
    # ==========================================================

    record: TradeIntelligenceRecord

    evidence: HistoricalEvidence

    recommendation: str

    confidence_before: float

    confidence_after: float

    explanation: str

    # ==========================================================
    # R2-005 intelligence state
    # ==========================================================

    timestamp: datetime | None = None

    direction: Direction = "NEUTRAL"

    conviction: float = 0.0

    opportunity_quality: float = 0.0

    execution_quality: float = 0.0

    risk_quality: float = 0.0

    # ==========================================================
    # Evidence
    # ==========================================================

    evidence_items: tuple[EvidenceItem, ...] = field(
        default_factory=tuple
    )

    evidence_summary: EvidenceSummary = field(
        default_factory=EvidenceSummary
    )

    # ==========================================================
    # Regime
    # ==========================================================

    regime: RegimeState = field(
        default_factory=RegimeState
    )

    # ==========================================================
    # Scenarios
    # ==========================================================

    primary_scenario: Scenario | None = None

    alternative_scenario: Scenario | None = None

    # ==========================================================
    # Invalidation / Reasons
    # ==========================================================

    invalidation: tuple[str, ...] = field(
        default_factory=tuple
    )

    reasons: tuple[str, ...] = field(
        default_factory=tuple
    )

    # ==========================================================
    # Data Quality
    # ==========================================================

    data_quality: DataQuality = field(
        default_factory=DataQuality
    )

    # ==========================================================
    # Contract
    # ==========================================================

    contract_version: str = "R2-005-A"

    def __post_init__(self) -> None:

        for name in (
            "confidence_before",
            "confidence_after",
            "conviction",
            "opportunity_quality",
            "execution_quality",
            "risk_quality",
        ):
            value = getattr(self, name)

            if not 0.0 <= value <= 100.0:
                raise ValueError(
                    f"{name} must be between 0 and 100"
                )

        if not self.contract_version.strip():
            raise ValueError(
                "contract_version must not be empty"
            )
