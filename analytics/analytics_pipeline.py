from analytics.gamma.gamma_flip import GammaFlipDetector
from analytics.gamma.gamma_wall import GammaWallDetector
from analytics.dealer.dealer_position_engine import DealerPositionEngine
from analytics.oi.oi_flow_engine import OIFlowEngine
from analytics.iv.iv_skew_analyzer import IVSkewAnalyzer
from analytics.iv.iv_smile_analyzer import IVSmileAnalyzer
from analytics.signal.probability_engine import ProbabilityEngine


class AnalyticsPipeline:

    def __init__(self):

        self.gamma_flip = GammaFlipDetector()
        self.gamma_wall = GammaWallDetector()
        self.dealer = DealerPositionEngine()
        self.oi = OIFlowEngine()
        self.iv_skew = IVSkewAnalyzer()
        self.iv_smile = IVSmileAnalyzer()
        self.probability = ProbabilityEngine()

    def run(
        self,
        greeks_engine,
        greeks_df,
        spot_price
    ):

        # ------------------------------
        # Gamma
        # ------------------------------

        flip = self.gamma_flip.detect(greeks_df)

        wall = self.gamma_wall.detect(greeks_df)

        # ------------------------------
        # Dealer
        # ------------------------------

        dealer = self.dealer.analyze(
            greeks_engine,
            greeks_df,
            flip,
            wall,
            spot_price
        )

        # ------------------------------
        # OI
        # ------------------------------

        oi = self.oi.analyze(greeks_df)

        # ------------------------------
        # IV
        # ------------------------------

        skew = self.iv_skew.analyze(greeks_df)

        smile = self.iv_smile.analyze(greeks_df)

        # ------------------------------
        # Probability
        # ------------------------------

        probability = self.probability.calculate(
            dealer,
            skew,
            smile
        )

        return {

            "dealer": dealer,

            "gamma_flip": flip,

            "gamma_wall": wall,

            "oi_flow": oi,

            "iv_skew": skew,

            "iv_smile": smile,

            "probability": probability

        }