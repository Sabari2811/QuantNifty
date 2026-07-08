from analytics.iv.iv_smile_analyzer import IVSmileAnalyzer

from providers.indmoney_provider import INDMoneyProvider
from engine.instrument_manager import InstrumentManager
from engine.market_data_manager import MarketDataManager
from engine.strike_selector import StrikeSelector
from engine.option_chain_manager import OptionChainManager
from engine.live_greeks_engine import LiveGreeksEngine


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

spot = market.get_spot_price("NIFTY")

expiry = instrument.get_nearest_weekly_expiry("NIFTY")

option_chain = chain.get_live_option_chain(
    "NIFTY",
    spot,
    levels=5
)

greeks = LiveGreeksEngine()

df = greeks.calculate_chain_greeks(
    option_chain,
    spot,
    expiry
)

result = IVSmileAnalyzer().analyze(df)

print("\n")
print("=" * 60)
print("IV SMILE")
print("=" * 60)

for key, value in result.items():
    print(f"{key:20}: {value}")