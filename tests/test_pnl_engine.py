from paper_trading.portfolio import PortfolioEngine
from paper_trading.pnl_engine import PnLEngine

from paper_trading.models import (
    PaperOrder,
    PaperPosition,
)

portfolio_engine = PortfolioEngine()

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

portfolio_engine.add_position(position, 142 * 75)

pnl = PnLEngine(portfolio_engine.portfolio)

print("Initial Portfolio")
print(portfolio_engine.summary())

print()

pnl.update_price(position, 150)

pnl.update_portfolio()

print("After Premium = 150")
print(portfolio_engine.summary())

print()

print("Portfolio Value")
print(pnl.portfolio_value())