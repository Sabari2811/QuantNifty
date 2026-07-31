import uuid

from paper_trading.models.order import PaperOrder


class PaperBroker:
    """
    Simulates broker execution.
    """

    def place_order(self, order: PaperOrder):

        order.order_id = str(uuid.uuid4())

        order.status = "EXECUTED"

        return order