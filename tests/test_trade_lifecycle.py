from paper_trading.broker import PaperBroker
from paper_trading.exit_engine import ExitEngine
from paper_trading.models import (
    PaperOrder,
    PaperPosition,
)
from paper_trading.pnl_engine import PnLEngine

broker = PaperBroker()

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
    current_price=142,
    stop_loss=106,
    target=191,
)

broker.portfolio_engine.add_position(
    position,
    142 * 75,
)

pnl = PnLEngine(
    broker.portfolio_engine.portfolio
)

exit_engine = ExitEngine()

# Simulate market movement

pnl.update_price(position, 195)
pnl.update_portfolio()

result = exit_engine.evaluate(position)

print(result)

if result["exit"]:

    broker.close_position(
        position,
        result["price"],
        result["reason"],
    )

# Refresh portfolio after position closed
pnl.update_portfolio()

print("\nPortfolio Summary")
print(broker.portfolio_engine.summary())

print("\nClosed Position")
print(position)

print("\nTrade Journal Summary")
print(broker.journal.summary())

print("\nTrade Records")
for trade in broker.journal.all_trades():
    print(trade)