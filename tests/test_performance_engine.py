from datetime import datetime

from paper_trading.journal import TradeJournal
from paper_trading.models import (
    PaperOrder,
    PaperPosition,
)

from performance.engine import (
    PerformanceEngine,
)

journal = TradeJournal()

# --------------------------------------------------
# Trade 1
# --------------------------------------------------

order = PaperOrder(
    order_id="1",
    signal="BUY CALL",
    option_type="CE",
    strike=24400,
    quantity=75,
    entry_price=100,
)

position = PaperPosition(order)

position.exit_price = 120
position.exit_time = datetime.now()
position.pnl = 1500

journal.record(
    position,
    "TARGET"
)

# --------------------------------------------------
# Trade 2
# --------------------------------------------------

order2 = PaperOrder(
    order_id="2",
    signal="BUY PUT",
    option_type="PE",
    strike=24300,
    quantity=75,
    entry_price=100,
)

position2 = PaperPosition(order2)

position2.exit_price = 90
position2.exit_time = datetime.now()
position2.pnl = -750

journal.record(
    position2,
    "STOP LOSS"
)

engine = PerformanceEngine(
    journal
)

metrics = engine.calculate()

print()

print("Performance Metrics")

print(metrics)

print()

print("Equity Curve")

capital = 500000

equity = [capital]

running = capital

for trade in journal.all_trades():

    running += trade.pnl

    equity.append(running)

print(equity)