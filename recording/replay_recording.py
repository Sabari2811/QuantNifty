from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class ReplayRecording:
    """
    Represents one recorded QuantNifty replay session.

    This is metadata only.

    It does NOT load any files.
    It does NOT parse JSON.
    It does NOT know about ReplaySession.

    It simply describes one recording discovered
    by SnapshotRepository.
    """

    # ==========================================================
    # Identity
    # ==========================================================

    date: str

    session_name: str

    folder: Path

    # ==========================================================
    # Runtime
    # ==========================================================

    timestamp: str

    cycle: int

    # ==========================================================
    # File Availability
    # ==========================================================

    runtime: bool

    analytics: bool

    decision: bool

    explanation: bool

    greeks: bool

    option_chain: bool

    manifest: bool

    # ==========================================================
    # Derived
    # ==========================================================

    @property
    def complete(self) -> bool:
        """
        Returns True when all expected files exist.
        """

        return all(

            (

                self.runtime,

                self.analytics,

                self.decision,

                self.explanation,

                self.greeks,

                self.option_chain,

                self.manifest,

            )

        )

    @property
    def display_name(self) -> str:
        """
        Friendly name for UI.
        """

        return f"{self.date} • {self.timestamp}"