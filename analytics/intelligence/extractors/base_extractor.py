from __future__ import annotations

from abc import ABC, abstractmethod


class BaseExtractor(ABC):
    """
    Base class for all Trade Intelligence extractors.

    Responsibilities
    ----------------
    - Read RuntimeContext
    - Populate a portion of TradeIntelligenceRecord

    Each extractor owns ONE domain only.
    """

    @abstractmethod
    def extract(
        self,
        ctx,
        record,
    ) -> None:
        """
        Populate part of the TradeIntelligenceRecord.

        Parameters
        ----------
        ctx
            RuntimeContext

        record
            TradeIntelligenceRecord

        Returns
        -------
        None
        """
        raise NotImplementedError