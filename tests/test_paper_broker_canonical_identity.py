from types import SimpleNamespace

from paper_trading.broker import PaperBroker


class Decision:
    valid = True
    signal = SimpleNamespace(name="BUY CALL")
    strategy_name = "TEST"

    trade = SimpleNamespace(
        option_type="CE",
        strike=24000,
        entry=100,
        stop_loss=80,
        target1=130,
        risk_reward=1.5,
        execution=SimpleNamespace(lot_size=75, lots=1),
    )


class Intent:
    client_order_id = "client-123"


class CanonicalPaperBroker(PaperBroker):
    def execute(self, decision):
        return super().execute(decision)


def test_existing_paper_broker_uses_canonical_client_order_id():
    broker = CanonicalPaperBroker()
    intent = Intent()

    decision = Decision()
    decision.execution_intent = intent

    position = broker.execute(decision)

    assert position is not None
    assert position.order.order_id == intent.client_order_id


def test_existing_paper_broker_generates_legacy_id_without_canonical_intent():
    broker = CanonicalPaperBroker()

    decision = Decision()
    decision.execution_intent = None

    position = broker.execute(decision)

    assert position is not None
    assert position.order.order_id
