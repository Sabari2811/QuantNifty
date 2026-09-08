"""Durable, fail-closed evidence for genuine live validation cycles."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class LiveCycleEvidence:
    timestamp: str
    provider: str
    provider_mode: str
    cycle_no: Any
    spot: Any
    option_chain_coverage: Any
    option_chain_integrity: Any
    runtime_status: Any
    trade_status: Any
    block_reason: Any
    provenance_freshness: Any
    brain_status: Any
    learning_status: Any
    persistence_status: Any
    evidence_state: str


def _is_live_provider(provider: Any, provider_mode: Any) -> bool:
    return (
        str(provider or "").strip().upper()
        in {"INDMONEY", "INDSTOCKS", "INDSTOCKS_PROVIDER"}
        and str(provider_mode or "").strip().upper() == "LIVE_PROVIDER"
    )


def build_live_cycle_evidence(
    ctx: Any,
    *,
    provider: str | None = None,
    provider_mode: str | None = None,
    brain_status: Any = None,
    learning_status: Any = None,
    persistence_status: Any = None,
) -> LiveCycleEvidence:
    """Build evidence; missing identity is never assumed to be live."""
    provenance = getattr(ctx, "data_provenance", None)
    option = getattr(provenance, "option_chain", None) if provenance else None
    timestamp = datetime.now(timezone.utc).isoformat()
    valid = _is_live_provider(provider, provider_mode)
    evidence_state = "VALID_LIVE" if valid else "INVALID_NOT_LIVE"
    return LiveCycleEvidence(
        timestamp=timestamp,
        provider=str(provider or "UNKNOWN"),
        provider_mode=str(provider_mode or "UNKNOWN"),
        cycle_no=getattr(ctx, "cycle_no", None),
        spot=getattr(ctx, "spot", None),
        option_chain_coverage=getattr(option, "coverage_status", None),
        option_chain_integrity=getattr(option, "integrity_status", None),
        runtime_status=getattr(ctx, "runtime_status", None),
        trade_status=getattr(ctx, "trade_status", None),
        block_reason=getattr(ctx, "trade_block_reason", None),
        provenance_freshness=getattr(provenance, "freshness_status", None) if provenance else None,
        brain_status=brain_status,
        learning_status=learning_status,
        persistence_status=persistence_status,
        evidence_state=evidence_state,
    )


class JsonlLiveEvidenceStore:
    """Append-only local evidence store."""

    def __init__(self, path: str | os.PathLike[str] | None = None):
        self.path = Path(path or os.getenv("LIVE_EVIDENCE_PATH", "runtime_data/live_validation.jsonl"))
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, evidence: LiveCycleEvidence) -> None:
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(asdict(evidence), default=str, sort_keys=True) + "\n")
            fh.flush()
            os.fsync(fh.fileno())

    def count(self) -> int:
        if not self.path.exists():
            return 0
        with self.path.open("r", encoding="utf-8") as fh:
            return sum(1 for line in fh if line.strip())
