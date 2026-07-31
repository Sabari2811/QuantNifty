from paper_trading.models import PaperOrder, PaperPosition
from paper_trading.exit_engine import ExitEngine

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

engine = ExitEngine()

print(engine.evaluate(position))

position.current_price = 100

print(engine.evaluate(position))

position.current_price = 195

print(engine.evaluate(position))