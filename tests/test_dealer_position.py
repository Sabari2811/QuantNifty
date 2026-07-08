from providers.indmoney_provider import INDMoneyProvider

from engine.instrument_manager import InstrumentManager
from engine.market_data_manager import MarketDataManager
from engine.strike_selector import StrikeSelector
from engine.option_chain_manager import OptionChainManager
from engine.live_greeks_engine import LiveGreeksEngine

from analytics.gamma_flip_detector import GammaFlipDetector
from analytics.gamma_wall_detector import GammaWallDetector
from analytics.dealer.dealer_position_engine import DealerPositionEngine


provider = INDMoneyProvider()
provider.connect()

instrument = InstrumentManager()
instrument.load_fno()

market = MarketDataManager(provider)

selector = StrikeSelector(instrument)

chain = OptionChainManager(
    provider,
    selector,
    instrument,
    market
)

spot = 24270.85

expiry = instrument.get_nearest_weekly_expiry("NIFTY")

option_chain = chain.get_live_option_chain(
    symbol="NIFTY",
    spot_price=spot,
    levels=5
)

greeks = LiveGreeksEngine()

df = greeks.calculate_chain_greeks(
    option_chain,
    spot,
    expiry
)

flip = GammaFlipDetector().detect(df)

wall = GammaWallDetector().detect(df)

dealer = DealerPositionEngine()

result = dealer.analyze(
    greeks,
    df,
    flip,
    wall,
    spot
)

print("\n")
print("=" * 70)
print("DEALER POSITION ENGINE")
print("=" * 70)

for key, value in result.items():
    print(f"{key:30}: {value}")