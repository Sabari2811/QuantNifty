from providers.indmoney_provider import INDMoneyProvider

from engine.instrument_manager import InstrumentManager
from engine.market_data_manager import MarketDataManager
from engine.strike_selector import StrikeSelector
from engine.option_chain_manager import OptionChainManager
from engine.oi_analyzer import OIAnalyzer


provider = INDMoneyProvider()
provider.connect()

instrument = InstrumentManager()

# Load F&O master
instrument.load("fno")

market = MarketDataManager(provider)

selector = StrikeSelector(instrument)

chain = OptionChainManager(
    provider=provider,
    strike_selector=selector,
    instrument_manager=instrument,
    market_manager=market
)

df = chain.get_live_option_chain(
    symbol="NIFTY",
    spot_price=24270.85,
    levels=5
)

print("\n========================")
print("OPTION CHAIN")
print("========================")
print(df)

analysis = OIAnalyzer().analyze(df)

print("\n========================")
print("OI ANALYSIS")
print("========================")

for key, value in analysis.items():
    print(f"{key:20}: {value}")