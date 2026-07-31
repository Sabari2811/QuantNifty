from decision.context import DecisionContext


class DecisionBuilder:
    """
    Converts MarketSnapshot into DecisionContext.

    This isolates the Decision Engine from the
    Analytics Pipeline structure.
    """

    def build(self, snapshot):

        ctx = DecisionContext()

        ctx.snapshot = snapshot

        # --------------------------------------
        # Analytics
        # --------------------------------------

        ctx.dealer = snapshot.dealer

        ctx.pcr = snapshot.pcr

        ctx.max_pain = snapshot.max_pain

        ctx.probability = snapshot.prediction

        ctx.institutional = snapshot.institutional

        # Dealer Flow (future)

        ctx.dealer_flow = snapshot.get(
            "dealer_flow",
            {}
        )

        # Liquidity (future)

        ctx.liquidity = snapshot.get(
            "liquidity",
            {}
        )

        # Gamma (future)

        ctx.gamma = {

            "flip": snapshot.dealer.get(
                "gamma_flip"
            ),

            "wall": snapshot.dealer.get(
                "gamma_wall"
            ),

            "call_wall": snapshot.dealer.get(
                "call_wall"
            ),

            "put_wall": snapshot.dealer.get(
                "put_wall"
            )
        }

        return ctx