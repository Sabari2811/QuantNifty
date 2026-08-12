from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True, slots=True)
class EvidenceFamily:
    """Canonical family used to prevent correlated evidence double-counting."""

    name: str
    aliases: tuple[str, ...]
    max_independent_weight: float = 1.0


class EvidenceIndependenceMatrix:
    """Maps individual evidence features into correlated evidence families."""

    _families: tuple[EvidenceFamily, ...] = (
        EvidenceFamily(
            name="GAMMA",
            aliases=(
                "gamma",
                "gex",
                "gamma_exposure",
                "net_gamma",
                "gamma_flip",
                "gamma_wall",
                "gamma_regime",
            ),
        ),
        EvidenceFamily(
            name="VOLATILITY",
            aliases=(
                "iv",
                "implied_volatility",
                "iv_rank",
                "iv_percentile",
                "iv_skew",
                "skew",
                "rr25",
                "risk_reversal",
                "volatility",
            ),
        ),
        EvidenceFamily(
            name="OI_FLOW",
            aliases=(
                "oi",
                "open_interest",
                "oi_change",
                "oi_flow",
                "open_interest_flow",
                "pcr",
            ),
        ),
        EvidenceFamily(
            name="DEALER",
            aliases=(
                "dealer",
                "dealer_flow",
                "dealer_gamma",
                "dealer_delta",
                "dex",
                "vanna",
                "charm",
            ),
        ),
        EvidenceFamily(
            name="GREEKS",
            aliases=(
                "greeks",
                "delta",
                "gamma_greek",
                "vega",
                "theta",
            ),
        ),
        EvidenceFamily(
            name="STRUCTURE",
            aliases=(
                "market_structure",
                "structure",
                "trend",
                "support_resistance",
                "breakout",
                "breakdown",
            ),
        ),
        EvidenceFamily(
            name="LIQUIDITY",
            aliases=(
                "liquidity",
                "volume",
                "volume_profile",
                "market_pressure",
            ),
        ),
        EvidenceFamily(
            name="TECHNICAL",
            aliases=(
                "technical",
                "rsi",
                "ema",
                "sma",
                "vwap",
                "atr",
                "adx",
                "macd",
            ),
        ),
        EvidenceFamily(
            name="SCORE",
            aliases=(
                "score",
                "institutional_score",
                "composite_score",
            ),
        ),
        EvidenceFamily(
            name="HISTORICAL",
            aliases=(
                "historical",
                "historical_evidence",
                "similarity",
		"historical_similarity",
                "memory",
                "market_memory",
            ),
        ),
    )

    def __init__(self) -> None:
        self._lookup: Mapping[str, EvidenceFamily] = {
            alias: family
            for family in self._families
            for alias in family.aliases
        }

    def classify(self, feature: str) -> EvidenceFamily:
        """Return the canonical family for an evidence feature."""

        key = self._normalize(feature)

        return self._lookup.get(
            key,
            EvidenceFamily(
                name="OTHER",
                aliases=(key,),
            ),
        )

    def families(self) -> tuple[EvidenceFamily, ...]:
        """Return all canonical evidence families."""

        return self._families

    @staticmethod
    def _normalize(value: str) -> str:
        return (
            value.strip()
            .lower()
            .replace("-", "_")
            .replace(" ", "_")
        )