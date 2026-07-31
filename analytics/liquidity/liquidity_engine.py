from analytics.liquidity.liquidity_wall_engine import (
    LiquidityWallEngine
)

from analytics.liquidity.liquidity_void_engine import (
    LiquidityVoidEngine
)

from analytics.liquidity.absorption_engine import (
    AbsorptionEngine
)

from analytics.liquidity.order_imbalance_engine import (
    OrderImbalanceEngine
)


class LiquidityEngine:
    """
    Master Liquidity Engine

    Combines

        • Liquidity Walls
        • Liquidity Voids
        • Absorption
        • Order Imbalance
    """

    def __init__(self):

        self.wall = LiquidityWallEngine()

        self.void = LiquidityVoidEngine()

        self.absorption = AbsorptionEngine()

        self.imbalance = OrderImbalanceEngine()

    def analyze(self, greeks_df):

        walls = self.wall.analyze(greeks_df)

        voids = self.void.analyze(greeks_df)

        absorption = self.absorption.analyze(greeks_df)

        imbalance = self.imbalance.analyze(greeks_df)

        return {

            "support": walls["support"],

            "resistance": walls["resistance"],

            "call_wall": walls["call_wall"],

            "put_wall": walls["put_wall"],

            "top_call_walls": walls["top_call_walls"],

            "top_put_walls": walls["top_put_walls"],

            "voids": voids,

            "absorption": absorption,

            "order_imbalance": imbalance

        }