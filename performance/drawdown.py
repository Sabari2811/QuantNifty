class DrawdownCalculator:
    """
    Calculates drawdown metrics
    from an equity curve.
    """

    @staticmethod
    def calculate(equity_curve):

        if not equity_curve:

            return {

                "max_drawdown": 0,

                "current_drawdown": 0,

                "peak_equity": 0,

                "ending_equity": 0,

            }

        peak = equity_curve[0]

        max_drawdown = 0

        current_drawdown = 0

        for value in equity_curve:

            if value > peak:

                peak = value

            drawdown = peak - value

            current_drawdown = drawdown

            max_drawdown = max(
                max_drawdown,
                drawdown
            )

        return {

            "max_drawdown": max_drawdown,

            "current_drawdown": current_drawdown,

            "peak_equity": peak,

            "ending_equity": equity_curve[-1],

        }