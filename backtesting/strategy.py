from dataclasses import dataclass

from backtesting.models import MarketCandle


@dataclass
class MarketContext:
    """
    Complete market state.

    Initially contains only OHLC.

    Will gradually expand to include:

        Option Chain
        Greeks
        OI
        IV
        Gamma
        Dealer Positioning
        Market Structure
        Liquidity
    """

    candle: MarketCandle

    option_chain: object = None

    greeks: object = None

    market_structure: object = None

    gamma: object = None

    delta: object = None

    iv: object = None

    oi: object = None