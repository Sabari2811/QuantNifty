from models.market_context import MarketContext

from analytics.expected_move.expected_move_engine import ExpectedMoveEngine

from analytics.signal.signal_engine import SignalEngine
from analytics.signal.trade_plan_engine import TradePlanEngine
from analytics.signal.risk_engine import RiskEngine
from analytics.dealer.dealer_position_engine import DealerPositionEngine
from analytics.dealer_flow.dealer_flow_engine import DealerFlowEngine
from analytics.dealer_flow.delta_exposure_engine import DeltaExposureEngine
from analytics.dealer_flow.vanna_engine import VannaEngine
from analytics.dealer_flow.charm_engine import CharmEngine
from analytics.scoring.score_engine import ScoreEngine
from analytics.technical_analysis_engine import TechnicalAnalysisEngine
from analytics.market_map_engine import MarketMapEngine

from analytics.max_pain.max_pain_engine import MaxPainEngine
from analytics.pcr.pcr_engine import PCREngine

from analytics.market_structure.market_structure_engine import (
    MarketStructureEngine
)

from analytics.gamma.gamma_exposure import GammaExposureEngine
from analytics.gamma.gamma_flip import GammaFlipDetector
from analytics.gamma.gamma_wall import GammaWallDetector

from analytics.oi.oi_flow_engine import OIFlowEngine

from analytics.iv.iv_skew_analyzer import IVSkewAnalyzer
from analytics.iv.iv_smile_analyzer import IVSmileAnalyzer

from analytics.volatility.atr_engine import ATREngine
from analytics.volatility.volatility_engine import VolatilityEngine
from analytics.strike.smart_strike_engine import SmartStrikeEngine

from analytics.signal.probability_engine import ProbabilityEngine

from analytics.liquidity.liquidity_engine import LiquidityEngine
from analytics.liquidity.liquidity_wall_engine import LiquidityWallEngine
from analytics.liquidity.liquidity_void_engine import LiquidityVoidEngine
from analytics.liquidity.absorption_engine import AbsorptionEngine
from analytics.liquidity.order_imbalance_engine import OrderImbalanceEngine

from core.logger import logger


class AnalyticsPipeline:

    def __init__(self):

        # =====================================================
        # Gamma
        # =====================================================

        self.gamma_exposure = GammaExposureEngine()
        self.gamma_flip = GammaFlipDetector()
        self.gamma_wall = GammaWallDetector()
        self.score_engine = ScoreEngine()
        self.technical = TechnicalAnalysisEngine()
        self.market_map = MarketMapEngine()

        # =====================================================
        # Dealer
        # =====================================================

        self.dealer = DealerPositionEngine()
        self.dealer_flow = DealerFlowEngine()

        # =====================================================
        # Exposure Engines
        # =====================================================

        self.delta = DeltaExposureEngine()

        self.vanna = VannaEngine()

        self.charm = CharmEngine()

        # =====================================================
        # Liquidity
        # =====================================================

        self.liquidity = LiquidityEngine()

        # =====================================================
        # OI
        # =====================================================

        self.oi = OIFlowEngine()

        # =====================================================
        # IV
        # =====================================================

        self.iv_skew = IVSkewAnalyzer()
        self.iv_smile = IVSmileAnalyzer()

        # =====================================================
        # Expected Move
        # =====================================================

        self.expected_move = ExpectedMoveEngine()

        self.max_pain = MaxPainEngine()

        self.pcr = PCREngine()

        self.market_structure = MarketStructureEngine()

        # =====================================================
        # ATR
        # =====================================================

        self.atr = ATREngine()

        self.volatility = VolatilityEngine()

        # =====================================================
        # Probability
        # =====================================================

        self.probability = ProbabilityEngine()

        # =====================================================
        # Signal
        # =====================================================

        self.signal_engine = SignalEngine()

        # =====================================================
        # Strike Selection
        # =====================================================

        self.smart_strike = SmartStrikeEngine()

        # =====================================================
        # Trade Plan
        # =====================================================

        self.trade_plan = TradePlanEngine()

        # =====================================================
        # Risk
        # =====================================================

        self.risk = RiskEngine()

    # ==========================================================
    # MAIN PIPELINE
    # ==========================================================

    def run(
        self,
        greeks_engine,
        greeks_df,
        spot_price,
        candles=None,
        previous_greeks_df=None,
    ):

        # =====================================================
        # Gamma
        # =====================================================

        greeks_df = self.gamma_exposure.calculate(
            greeks_df
        )

        flip = self.gamma_flip.detect(
            greeks_df
        )

        wall = self.gamma_wall.detect(
            greeks_df
        )

        # =====================================================
        # Dealer
        # =====================================================

        dealer = self.dealer.analyze(
            greeks_engine,
            greeks_df,
            flip,
            wall,
            spot_price
        )

        # =====================================================
        # Dealer Flow Inputs
        # =====================================================

        greeks_df, delta_summary = self.delta.calculate(
            greeks_df
        )

        greeks_df, vanna_summary = self.vanna.calculate(
            greeks_df,
            spot_price
        )

        greeks_df, charm_summary = self.charm.calculate(
            greeks_df,
            spot_price
        )

        dealer_flow = self.dealer_flow.analyze(
            delta_summary,
            vanna_summary,
            charm_summary
        )

        # =====================================================
        # Liquidity
        # =====================================================

        liquidity = self.liquidity.analyze(
            greeks_df
        )

        # =====================================================
        # OI
        # =====================================================

        oi_result = self.oi.analyze(
            greeks_df,
            previous_greeks_df,
        )

        logger.info(
            "OI RESULT | summary=%s",
            oi_result["summary"],
        )

        logger.debug(
            "OI RESULT | columns=%s",
            oi_result["table"].columns.tolist(),
        )

        # Updated greeks dataframe
        # (contains CE_FLOW / PE_FLOW)

        greeks_df = oi_result["table"]

        # OI analytics (summary + table)

        oi = oi_result

        # =====================================================
        # IV
        # =====================================================

        skew = self.iv_skew.analyze(
            greeks_df
        )

        smile = self.iv_smile.analyze(
            greeks_df
        )

        # =====================================================
        # Expected Move
        # =====================================================

        expected_move = self.expected_move.calculate(
            greeks_df,
            spot_price
        )

        max_pain = self.max_pain.calculate(
            greeks_df
        )

        pcr = self.pcr.calculate(
            greeks_df
        )

        # =====================================================
        # ATR
        # =====================================================

        atr = self.atr.analyze(
            greeks_df
        )

        volatility = self.volatility.analyze(
            iv_skew=skew,
            iv_smile=smile,
            expected_move=expected_move,
            atr=atr,
            spot=spot_price,
        )

        market_structure = self.market_structure.analyze(
            greeks_df,
            dealer,
            pcr,
            expected_move
        )

        # =====================================================
        # Technical Analysis
        # =====================================================

        if candles is not None:

            technical = self.technical.analyze(
                candles
            )

        else:

            technical = {
                "atr": {},
                "ema": {},
                "rsi": {},
                "vwap": {},
                "adx": {}
            }

        # =====================================================
        # Probability
        # =====================================================

        probability = self.probability.calculate(
            dealer,
            market_structure,
            pcr,
            skew,
            technical
        )

        # =====================================================
        # Signal
        # =====================================================

        signal = self.signal_engine.generate(
            dealer,
            probability,
            spot_price
        )

        # =====================================================
        # Institutional Score
        # =====================================================

        institutional_score = self.score_engine.calculate(
            dealer=dealer,
            dealer_flow=dealer_flow,
            liquidity=liquidity,
            market_structure=market_structure,
            pcr=pcr,
            expected_move=expected_move,
            iv_skew=skew,
            iv_smile=smile,
            atr=atr,
            signal=signal,
            spot=spot_price
        )

        # =====================================================
        # Smart Strike
        # =====================================================

        smart_strike = self.smart_strike.analyze(
            greeks_df=greeks_df,
            signal=signal,
            dealer=dealer,
            probability=probability,
            atr=atr,
            spot=spot_price
        )

        # =====================================================
        # Trade Plan
        # =====================================================

        trade_plan = self.trade_plan.generate(
            signal=signal,
            dealer=dealer,
            spot=spot_price,
            atr=atr,
            smart_strike=smart_strike
        )

        # =====================================================
        # Risk
        # =====================================================

        risk = self.risk.generate(
            trade_plan
        )

        # =====================================================
        # Context
        # =====================================================

        context = MarketContext()

        context.spot = spot_price
        context.greeks = greeks_df

        context.dealer = dealer
        context.dealer_flow = dealer_flow

        context.liquidity = liquidity

        context.gamma_flip = flip
        context.gamma_wall = wall

        context.oi_flow = oi

        context.iv_skew = skew
        context.iv_smile = smile

        context.expected_move = expected_move
        context.max_pain = max_pain
        context.pcr = pcr
        context.market_structure = market_structure

        context.atr = atr
        context.volatility = volatility
        context.technical = technical

        context.probability = probability
        context.signal = signal
        context.institutional_score = institutional_score
        context.smart_strike = smart_strike
        context.trade_plan = trade_plan
        context.risk = risk

        # =====================================================
        # Output
        # =====================================================

        market_map = self.market_map.build(
            analytics={
                "dealer": dealer,

                "gamma_levels": {
                    "gamma_flip": flip.get(
                        "gamma_flip",
                        "-"
                    ),

                    "gamma_wall": wall.get(
                        "gamma_wall",
                        "-"
                    ),

                    "call_wall": wall.get(
                        "call_wall",
                        "-"
                    ),

                    "put_wall": wall.get(
                        "put_wall",
                        "-"
                    )
                },

                "expected_move": expected_move,

                "max_pain": max_pain
            },

            spot=spot_price

        )

        # Market map is produced after the initial context assembly, so
        # assign it explicitly rather than relying on a dynamic attribute.
        context.market_map = market_map

        return {

            "context": context,

            "dealer": dealer,

            "dealer_flow": dealer_flow,

            "liquidity": liquidity,

            "gamma_flip": flip,

            "gamma_wall": wall,

            "oi_flow": oi,

            "iv_skew": skew,

            "iv_smile": smile,

            "expected_move": expected_move,

            "max_pain": max_pain,

            "pcr": pcr,

            "market_structure": market_structure,

            "atr": atr,

            "volatility": volatility,

            "probability": probability,

            "signal": signal,

            "smart_strike": smart_strike,

            "trade_plan": trade_plan,

            "risk": risk,

            "institutional_score": institutional_score,

            "technical": technical,

            "market_map": market_map,

            "greeks": greeks_df

        }