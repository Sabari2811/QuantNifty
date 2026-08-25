from __future__ import annotations

import json
from dataclasses import fields, is_dataclass
from datetime import datetime
from pathlib import Path
from types import UnionType
from typing import Any, Union, get_args, get_origin, get_type_hints

import pandas as pd

from analytics.intelligence.result import IntelligenceResult
from core.data_provenance import RuntimeDataProvenance
from recording.snapshot_manifest import SnapshotManifest
from simulation.replay_snapshot import ReplaySnapshot


class ReplayLoader:
    """Loads a recorded snapshot from disk into a ReplaySnapshot."""

    def load(self, folder: str | Path) -> ReplaySnapshot:
        folder = Path(folder)
        manifest = SnapshotManifest.load(folder)
        snapshot = ReplaySnapshot()

        snapshot.runtime = self._load_json(folder / manifest.runtime)
        snapshot.analytics = self._load_json(folder / manifest.analytics)
        snapshot.decision = self._load_json(folder / manifest.decision)
        snapshot.explanation = self._load_json(folder / manifest.explanation)
        intelligence_payload = self._load_json(folder / manifest.intelligence)
        snapshot.intelligence = self._restore_intelligence(intelligence_payload)
        snapshot.option_chain = self._load_dataframe(folder / manifest.option_chain)
        snapshot.greeks = self._load_dataframe(folder / manifest.greeks)
        snapshot.data_provenance = RuntimeDataProvenance.from_dict(
            snapshot.runtime.get("data_provenance")
        )

        return snapshot

    @staticmethod
    def _restore_intelligence(payload: dict) -> IntelligenceResult | dict:
        """Restore canonical IntelligenceResult while preserving legacy payloads."""
        if not payload:
            return {}
        return ReplayLoader._from_typed_dataclass(payload, IntelligenceResult)

    @staticmethod
    def _from_typed_dataclass(payload: Any, target_type: Any) -> Any:
        """Recursively rebuild dataclass, collection, union, and datetime types."""
        if payload is None:
            return None

        origin = get_origin(target_type)
        args = get_args(target_type)

        if origin in (Union, UnionType):
            non_none = [arg for arg in args if arg is not type(None)]
            if payload is None:
                return None
            for candidate in non_none:
                try:
                    return ReplayLoader._from_typed_dataclass(payload, candidate)
                except (TypeError, ValueError, KeyError):
                    continue
            return payload

        if origin in (list, tuple):
            item_type = args[0] if args else Any
            values = [ReplayLoader._from_typed_dataclass(value, item_type) for value in payload]
            return tuple(values) if origin is tuple else values

        if origin is dict:
            key_type, value_type = args if len(args) == 2 else (Any, Any)
            return {
                ReplayLoader._from_typed_dataclass(key, key_type): ReplayLoader._from_typed_dataclass(value, value_type)
                for key, value in payload.items()
            }

        if target_type is datetime:
            return datetime.fromisoformat(payload) if isinstance(payload, str) else payload

        if target_type is Any:
            return payload

        if isinstance(target_type, type) and is_dataclass(target_type):
            if not isinstance(payload, dict):
                raise TypeError(f"Expected object for {target_type.__name__}")
            hints = get_type_hints(target_type)
            kwargs = {}
            for field in fields(target_type):
                if field.name in payload:
                    field_type = hints.get(field.name, field.type)
                    kwargs[field.name] = ReplayLoader._from_typed_dataclass(
                        payload[field.name], field_type
                    )
            return target_type(**kwargs)

        return payload

    def _load_json(self, path: Path) -> dict:
        if not path.exists():
            return {}
        with open(path, "r", encoding="utf-8") as fp:
            return json.load(fp)

    def _load_dataframe(self, path: Path) -> pd.DataFrame:
        if not path.exists():
            return pd.DataFrame()
        return pd.read_parquet(path)
