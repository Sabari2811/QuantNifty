from datetime import datetime, timedelta

from backtesting.models import MarketCandle
from backtesting.replay_engine import ReplayEngine
from backtesting.backtest_engine import BacktestEngine

from strategies.smc_strategy import SMCStrategy


candles = []

start = datetime(2026, 1, 1, 9, 15)

price = 24000

for i in range(10):

    candles.append(
        MarketCandle(
            timestamp=start + timedelta(minutes=5 * i),
            open=price,
            high=price + 20,
            low=price - 10,
            close=price + 5,
            volume=1000,
        )
    )

    price += 20


replay = ReplayEngine(candles)

strategy = SMCStrategy()

engine = BacktestEngine(
    replay_engine=replay,
    strategy=strategy,
)

engine.run()