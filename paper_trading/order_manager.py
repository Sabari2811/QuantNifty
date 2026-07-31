from paper_trading.position import Position


class OrderManager:
    """
    Creates paper positions from the
    Decision Engine.
    """

    def __init__(self, portfolio_engine):

        self.portfolio_engine = portfolio_engine

    # =====================================================
    # MAIN
    # =====================================================

    def place_order(
        self,
        decision,
        snapshot,
    ):

        signal = decision.signal.name

        if signal == "WAIT":
            return None

        execution = decision.execution

        investment = (
            execution.entry_price
            * execution.quantity
        )

        position = Position(

            symbol=snapshot.symbol,

            option_type=execution.option_type,

            strike=execution.strike,

            quantity=execution.quantity,

            entry_price=execution.entry_price,

            current_price=execution.entry_price,

            stop_loss=execution.stop_loss,

            target=execution.target,

            invested_amount=investment,

        )

        self.portfolio_engine.add_position(

            position,

            investment,

        )

        return position