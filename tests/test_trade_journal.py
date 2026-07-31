from datetime import datetime

from paper_trading.journal import TradeJournal
from paper_trading.models import (
    PaperOrder,
    PaperPosition,
)

journal = TradeJournal()

order = PaperOrder(
    order_id="1",
    signal="BUY CALL",
    option_type="CE",
    strike=24400,
    quantity=75,
    entry_price=142,
)

position = PaperPosition(
    order=order,
    current_price=191,
    stop_loss=106,
    target=191,
)

position.closed = True
position.exit_price = 191
position.exit_time = datetime.now()
position.pnl = 3675

record = journal.record(
    position,
    "TARGET"
)

print(record)

print()

print(journal.summary())

print()

print(journal.all_trades())