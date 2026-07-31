from __future__ import annotations

from collections import defaultdict

from analytics.intelligence.models import TradeIntelligenceRecord


class MarketMemory:
    """
    Stores historical Trade Intelligence records.

    Responsibilities
    ----------------
    - Store records
    - Query records
    - Retrieve statistics
    - Support similarity search
    - Provide datasets for ML

    This class deliberately performs
    NO feature extraction.
    """

    def __init__(self):

        self._records: list[TradeIntelligenceRecord] = []

        self._index_by_signal = defaultdict(list)

        self._index_by_outcome = defaultdict(list)

    # ====================================================
    # Storage
    # ====================================================

    def add(
        self,
        record: TradeIntelligenceRecord,
    ):

        self._records.append(record)

        self._index_by_signal[
            record.signal
        ].append(record)

        self._index_by_outcome[
            record.outcome
        ].append(record)

    # ====================================================
    # Access
    # ====================================================

    @property
    def records(self):

        return self._records

    @property
    def size(self):

        return len(self._records)

    # ====================================================
    # Queries
    # ====================================================

    def by_signal(
        self,
        signal,
    ):

        return self._index_by_signal.get(
            signal,
            [],
        )

    def by_outcome(
        self,
        outcome,
    ):

        return self._index_by_outcome.get(
            outcome,
            [],
        )

    # ====================================================
    # Statistics
    # ====================================================

    def summary(self):

        return {

            "records": self.size,

            "buy": len(
                self.by_signal("BUY")
            ),

            "sell": len(
                self.by_signal("SELL")
            ),

            "wait": len(
                self.by_signal("WAIT")
            ),

            "wins": len(
                self.by_outcome("WIN")
            ),

            "losses": len(
                self.by_outcome("LOSS")
            ),

        }

    # ====================================================
    # Export
    # ====================================================

    def clear(self):

        self._records.clear()

        self._index_by_signal.clear()

        self._index_by_outcome.clear()