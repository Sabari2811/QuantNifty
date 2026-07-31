from __future__ import annotations

from dataclasses import dataclass

from analytics.intelligence.models import TradeIntelligenceRecord
from analytics.intelligence.evidence.models import HistoricalEvidence


@dataclass(slots=True)
class IntelligenceResult:
    """
    Final intelligence package returned to the UI.

    This object hides all internal intelligence
    implementation details.

    UI should consume THIS object only.
    """

    #
    # Current Market
    #

    record: TradeIntelligenceRecord

    #
    # Historical Evidence
    #

    evidence: HistoricalEvidence

    #
    # Final Recommendation
    #

    recommendation: str

    confidence_before: float

    confidence_after: float

    explanation: str