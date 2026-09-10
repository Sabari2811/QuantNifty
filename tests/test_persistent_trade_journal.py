from datetime import datetime

from paper_trading.models import PaperPosition, PaperOrder
from paper_trading.persistent_journal import PersistentTradeJournal


def _position():
    return PaperPosition(
        order=PaperOrder(
            order_id="test-order-1",
            signal="BUY CALL",
            option_type="CE",
            strike=25000,
            quantity=75,
            entry_price=100.0,
            order_time=datetime(2026, 9, 10, 10, 0, 0),
        ),
        exit_price=120.0,
        pnl=1500.0,
        closed=True,
        exit_time=datetime(2026, 9, 10, 10, 5, 0),
        confidence=80.0,
        risk_reward=2.0,
        strategy_name="TEST",
    )


def test_persistent_trade_journal_round_trip(tmp_path):
    url = f"sqlite:///{tmp_path / 'trades.db'}"
    journal = PersistentTradeJournal(database_url=url)
    journal.record(_position(), "TARGET")
    assert journal.summary()["total_trades"] == 1
    assert journal.summary()["total_pnl"] == 1500.0
    journal.close()

    restored = PersistentTradeJournal(database_url=url)
    trades = restored.all_trades()
    assert len(trades) == 1
    assert trades[0].order_id == "test-order-1"
    assert trades[0].pnl == 1500.0
    assert restored.summary()["winning_trades"] == 1
    restored.close()
