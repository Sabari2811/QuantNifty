from __future__ import annotations

"""
==========================================================
Composition Root

Creates every long-lived dependency exactly once.

Nothing else in QuantNifty should instantiate these
objects directly.

==========================================================
"""

from analytics.intelligence.feature_extractor import FeatureExtractor
from analytics.intelligence.memory_engine import MarketMemory
from analytics.intelligence.similarity.similarity_engine import SimilarityEngine
from analytics.intelligence.evidence.evidence_engine import EvidenceEngine

from application.intelligence_service import IntelligenceService

from paper_trading.broker import PaperBroker


class CompositionRoot:

    def __init__(self):

        #
        # Infrastructure
        #

        self.paper_broker = PaperBroker()

        #
        # Intelligence
        #

        self.feature_extractor = FeatureExtractor()

        self.market_memory = MarketMemory()

        self.similarity_engine = SimilarityEngine()

        self.evidence_engine = EvidenceEngine(
            similarity_engine=self.similarity_engine
        )

        #
        # Application Services
        #

        self.intelligence_service = IntelligenceService(
            feature_extractor=self.feature_extractor,
            market_memory=self.market_memory,
            evidence_engine=self.evidence_engine,
        )