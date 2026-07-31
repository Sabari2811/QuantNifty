from datetime import datetime

from backtesting.models import MarketCandle
from backtesting.strategy import MarketContext

from strategies.smc_strategy import SMCStrategy


candle = MarketCandle(

    timestamp=datetime.now(),

    open=24000,

    high=24040,

    low=23980,

    close=24025,

    volume=10000,

)

context = MarketContext(

    candle=candle

)

strategy = SMCStrategy()

decision = strategy.on_market_update(

    context

)

print()

print("Decision")

print(decision)