from datetime import datetime, timedelta

from backtesting.models import MarketCandle
from backtesting.replay_engine import ReplayEngine

candles = []

start = datetime(2026, 1, 1, 9, 15)

price = 24000

for i in range(5):

    candles.append(

        MarketCandle(

            timestamp=start + timedelta(minutes=5 * i),

            open=price,

            high=price + 15,

            low=price - 10,

            close=price + 5,

            volume=1000 + i * 100,

        )

    )

    price += 20

engine = ReplayEngine(candles)

while engine.has_next():

    candle = engine.next()

    print(candle)

print("\nReplay Completed")

engine.reset()

print("\nReset Successful:", engine.has_next())