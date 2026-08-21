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
from analytics.intelligence.similarity.similarity_engine import (
    SimilarityEngine,
)
from analytics.intelligence.evidence.evidence_engine import EvidenceEngine
from analytics.intelligence.gate import IntelligenceGate

from application.intelligence_service import IntelligenceService

from execution.trade_execution_pipeline import TradeExecutionPipeline

from paper_trading.broker import PaperBroker

from risk.risk_manager import RiskManager


class CompositionRoot:

    def __init__(self):

        # ======================================================
        # Infrastructure
        # ======================================================

        self.paper_broker = PaperBroker()

        # ======================================================
        # Intelligence Infrastructure
        # ======================================================

        self.similarity_engine = SimilarityEngine()

        self.feature_extractor = FeatureExtractor()

        self.market_memory = MarketMemory()

        self.evidence_engine = EvidenceEngine(
            similarity_engine=self.similarity_engine
        )

        self.intelligence_gate = IntelligenceGate()

        # ======================================================
        # Application Services
        # ======================================================

        self.intelligence_service = IntelligenceService(
            feature_extractor=self.feature_extractor,
            market_memory=self.market_memory,
            evidence_engine=self.evidence_engine,
        )

        # ======================================================
        # Risk
        # ======================================================

        self.risk_manager = RiskManager()

        # ======================================================
        # Execution
        # ======================================================

        self.trade_pipeline = TradeExecutionPipeline(
            paper_broker=self.paper_broker,
            risk_manager=self.risk_manager,
            intelligence_gate=self.intelligence_gate,
        )