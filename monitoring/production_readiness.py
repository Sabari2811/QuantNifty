"""Fail-closed production configuration readiness checks.

This module reports deployment prerequisites only. It never certifies live-market
behavior; genuine live evidence remains a separate validation gate.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import os
from typing import Any


@dataclass(frozen=True)
class ProductionReadiness:
    live_provider_configured: bool
    live_validation_enabled: bool
    brain_database_configured: bool
    evidence_database_configured: bool
    durable_persistence_configured: bool
    ready_for_production_infrastructure: bool


def build_production_readiness(env: dict[str, Any] | None = None) -> ProductionReadiness:
    values = env if env is not None else os.environ
    provider_configured = bool(str(values.get("APITOKEN", "") or "").strip())
    validation_enabled = str(values.get("LIVE_VALIDATION_MODE", "") or "").strip().lower() == "true"
    brain_db = bool(str(values.get("BRAIN_DATABASE_URL", "") or "").strip())
    evidence_db = bool(str(values.get("LIVE_EVIDENCE_DATABASE_URL", "") or "").strip())
    durable = brain_db and evidence_db

    # Infrastructure readiness is deliberately stricter than mere code
    # availability. It still does not imply that live data has been observed.
    ready = provider_configured and validation_enabled and durable
    return ProductionReadiness(
        live_provider_configured=provider_configured,
        live_validation_enabled=validation_enabled,
        brain_database_configured=brain_db,
        evidence_database_configured=evidence_db,
        durable_persistence_configured=durable,
        ready_for_production_infrastructure=ready,
    )


def production_readiness_as_dict(env: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return a safe serializable configuration snapshot without secrets."""
    return asdict(build_production_readiness(env))
