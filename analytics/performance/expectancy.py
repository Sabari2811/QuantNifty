class Expectancy:
    """
    Calculates trading expectancy.

    Formula:

        (Win Rate × Average Win)
        -
        (Loss Rate × Average Loss)
    """

    def calculate(

        self,

        win_rate,

        loss_rate,

        average_win,

        average_loss

    ):

        expectancy = (

            (win_rate / 100) * average_win

            -

            (loss_rate / 100) * average_loss

        )

        return round(

            expectancy,

            2

        )