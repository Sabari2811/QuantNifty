class TerminalDashboard:
    """
    Displays QuantNifty output
    in the terminal.
    """

    def __init__(self):
        pass

    def show(self, analytics):

        print()

        print("=" * 80)
        print("QUANTNIFTY LIVE")
        print("=" * 80)

        print()

        print("Decision")

        print(
            analytics.get(
                "decision",
                {}
            )
        )

        print()

        print("Probability")

        print(
            analytics.get(
                "probability",
                {}
            )
        )

        print()

        print("Dealer")

        print(
            analytics.get(
                "dealer",
                {}
            )
        )

        print()

        print("Regime")

        print(
            analytics.get(
                "market_regime",
                {}
            )
        )