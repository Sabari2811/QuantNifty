from backtesting.backtest_engine import BacktestEngine


class FakePaperBroker:
    def __init__(self):
        self.portfolio = {}
        self.journal = []
        self.performance = {}
        self.updated_option_chains = []

    def update_positions(self, option_chain):
        self.updated_option_chains.append(option_chain)


class FakePipeline:
    def __init__(self):
        self.paper_broker = FakePaperBroker()
        self.processed = []

    def process(self, decision, snapshot, runtime_config=None):
        self.processed.append(
            {
                "decision": decision,
                "snapshot": snapshot,
                "runtime_config": runtime_config,
            }
        )

        return {
            "decision": decision,
            "snapshot": snapshot,
        }


class FakeAdapter:
    def __init__(self):
        self.contexts = []

    def from_context(self, ctx):
        self.contexts.append(ctx)
        return f"decision-{len(self.contexts)}"


class FakeReplayController:
    """
    Minimal structural test double for the current BacktestEngine API.

    BacktestEngine only requires:
        - has_next()
        - next()
    """

    def __init__(self, contexts):
        self.contexts = list(contexts)
        self.index = 0

    def has_next(self):
        return self.index < len(self.contexts)

    def next(self):
        if not self.has_next():
            return None

        ctx = self.contexts[self.index]
        self.index += 1
        return ctx


def test_backtest_engine_runs_replay_through_pipeline():

    contexts = [
        {"timestamp": "2026-01-01T09:15:00", "option_chain": []},
        {"timestamp": "2026-01-01T09:20:00", "option_chain": []},
        {"timestamp": "2026-01-01T09:25:00", "option_chain": []},
    ]

    controller = FakeReplayController(contexts)

    engine = BacktestEngine(controller)

    fake_adapter = FakeAdapter()
    fake_pipeline = FakePipeline()

    engine.adapter = fake_adapter
    engine.pipeline = fake_pipeline

    result = engine.run()

    assert len(fake_adapter.contexts) == 3
    assert fake_adapter.contexts == contexts

    assert len(fake_pipeline.processed) == 3

    assert fake_pipeline.processed[0]["decision"] == "decision-1"
    assert fake_pipeline.processed[1]["decision"] == "decision-2"
    assert fake_pipeline.processed[2]["decision"] == "decision-3"

    assert len(
        fake_pipeline.paper_broker.updated_option_chains
    ) == 3

    assert result["portfolio"] == {}
    assert result["journal"] == []
    assert result["performance"] == {}
