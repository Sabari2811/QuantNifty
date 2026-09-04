from __future__ import annotations

from enum import Enum


class ExecutionMode(str, Enum):
    PAPER = "PAPER"
    LIVE = "LIVE"
