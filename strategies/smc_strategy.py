from strategies.base_strategy import BaseStrategy

from signals.models import (
    StrategySignal,
    SignalAction,
)


class SMCStrategy(BaseStrategy):

    def __init__(self):

        self.counter = 0

    def on_market_update(self, market_context):

        self.counter += 1

        candle = market_context.candle

        print(

            f"Candle {self.counter}"

            f" Close={candle.close}"

        )

        if self.counter == 3:

            return StrategySignal(

                action=SignalAction.BUY,

                strategy_name="SMC",

                confidence=82,

                reason="Demo Bullish Setup",

                quantity=1,

                stop_loss=23980,

                target=24120,

                metadata={

                    "session": "Morning",

                    "setup": "Bullish OB"

                }

            )

        return None