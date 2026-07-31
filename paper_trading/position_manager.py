from paper_trading.models.position import Position


class PositionManager:
    """
    Maintains all open paper positions.
    """

    def __init__(self):

        self.positions = []

    def add(self, position: Position):

        self.positions.append(position)

    def get_open_positions(self):

        return self.positions