from analytics.gamma.gamma_flip import GammaFlipDetector

from analytics.greeks.greeks_analyzer import GreeksAnalyzer

from engine.option_chain_manager import OptionChainManager
from engine.market_data_manager import MarketDataManager
from engine.instrument_manager import InstrumentManager
from engine.strike_selector import StrikeSelector
from engine.live_greeks_engine import LiveGreeksEngine

from providers.indmoney_provider import INDMoneyProvider


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

option_chain = chain.get_live_option_chain(
    symbol="NIFTY",
    spot_price=spot,
    levels=5
)

expiry = instrument.get_nearest_weekly_expiry("NIFTY")

greeks = LiveGreeksEngine()

greeks_df = greeks.calculate_chain_greeks(
    option_chain,
    spot,
    expiry
)

analyzer = GreeksAnalyzer()

greeks_df = analyzer.enrich(
    greeks_df,
    spot
)

flip = GammaFlipDetector()

result = flip.find_flip(greeks_df)

print("\n")
print("=" * 60)
print("GAMMA FLIP")
print("=" * 60)

print(result)
