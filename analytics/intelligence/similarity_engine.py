"""Compatibility facade for the canonical intelligence similarity engine.

The implementation lives under ``analytics.intelligence.similarity``. This
module remains import-compatible with older callers while eliminating the
legacy NotImplementedError stub.
"""
from __future__ import annotations

from analytics.intelligence.similarity.similarity_engine import SimilarityEngine

__all__ = ["SimilarityEngine"]
