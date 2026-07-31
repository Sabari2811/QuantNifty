from __future__ import annotations

from analytics.intelligence.models import TradeIntelligenceRecord

from analytics.intelligence.extractors.market import MarketExtractor
from analytics.intelligence.extractors.greeks import GreeksExtractor
from analytics.intelligence.extractors.dealer import DealerExtractor
from analytics.intelligence.extractors.decision import DecisionExtractor
from analytics.intelligence.extractors.trade import TradeExtractor


class FeatureExtractor:
    """
    Builds a TradeIntelligenceRecord from RuntimeContext.

    Each extractor owns one domain only.
    """

    def __init__(self):

        self.extractors = [

            MarketExtractor(),

            GreeksExtractor(),

            DealerExtractor(),

            DecisionExtractor(),

            TradeExtractor(),

        ]

    def extract(
        self,
        ctx,
    ) -> TradeIntelligenceRecord:

        record = TradeIntelligenceRecord()

        for extractor in self.extractors:

            extractor.extract(
                ctx,
                record,
            )

        return record