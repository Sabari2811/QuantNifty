from analytics.scoring.dealer_score import DealerScore
from analytics.scoring.liquidity_score import LiquidityScore
from analytics.scoring.gamma_score import GammaScore
from analytics.scoring.structure_score import StructureScore
from analytics.scoring.volatility_score import VolatilityScore
from analytics.scoring.institutional_score import InstitutionalScore


class ScoreEngine:
    """
    Master Institutional Scoring Engine
    """

    def __init__(self):

        self.dealer = DealerScore()
        self.liquidity = LiquidityScore()
        self.gamma = GammaScore()
        self.structure = StructureScore()
        self.volatility = VolatilityScore()
        self.institutional = InstitutionalScore()

    def calculate(

        self,

        dealer,

        dealer_flow,

        liquidity,

        market_structure,

        pcr,

        expected_move,

        iv_skew,

        iv_smile,

        atr,

        spot,

        signal=None

    ):

        # -----------------------------------------
        # Backward Compatibility
        # -----------------------------------------

        if signal is None:

            signal = {

                "signal": "NO TRADE"

            }

        # -----------------------------------------
        # Dealer
        # -----------------------------------------

        dealer_score = self.dealer.calculate(

            dealer,

            dealer_flow,

            signal

        )

        # -----------------------------------------
        # Liquidity
        # -----------------------------------------

        liquidity_score = self.liquidity.calculate(

            liquidity,

            signal,

            spot

        )

        # -----------------------------------------
        # Gamma
        # -----------------------------------------

        gamma_score = self.gamma.calculate(

            dealer,

            signal

        )

        # -----------------------------------------
        # Structure
        # -----------------------------------------

        structure_score = self.structure.calculate(

            market_structure,

            pcr,

            expected_move,

            signal,

            spot

        )

        # -----------------------------------------
        # Volatility
        # -----------------------------------------

        volatility_score = self.volatility.calculate(

            dealer,

            iv_skew,

            iv_smile,

            atr,

            signal

        )

        # -----------------------------------------
        # Institutional Score
        # -----------------------------------------

        institutional = self.institutional.calculate(

            dealer_score,

            liquidity_score,

            gamma_score,

            structure_score,

            volatility_score

        )

        return {

            "institutional": institutional,

            "dealer_score": dealer_score,

            "liquidity_score": liquidity_score,

            "gamma_score": gamma_score,

            "structure_score": structure_score,

            "volatility_score": volatility_score

        }