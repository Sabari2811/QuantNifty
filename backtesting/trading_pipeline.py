from decision.execution.execution_engine import ExecutionEngine
from paper_trading.broker import PaperBroker


class TradingPipeline:
    """
    Connects Strategy -> Execution -> Paper Broker.

    The pipeline does not make trading decisions.
    It only routes validated decisions through the
    existing QuantNifty infrastructure.
    """

    def __init__(self):

        self.execution_engine = ExecutionEngine()
        self.paper_broker = PaperBroker()

    def process(
        self,
        decision,
        snapshot,
        runtime_config=None,
    ):
        """
        Execute one trading decision.
        """

        decision = self.execution_engine.prepare(
            decision,
            snapshot,
            runtime_config,
        )

        if not decision.valid:
            return None

        return self.paper_broker.execute(decision)