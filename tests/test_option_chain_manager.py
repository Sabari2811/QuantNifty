from providers.indmoney_provider import INDMoneyProvider

from engine.instrument_manager import InstrumentManager
from engine.market_data_manager import MarketDataManager
from engine.strike_selector import StrikeSelector
from engine.option_chain_manager import OptionChainManager

provider = INDMoneyProvider()
provider.connect()

instrument = InstrumentManager()

market = MarketDataManager(provider)

selector = StrikeSelector(instrument)

chain = OptionChainManager(
    provider,
    selector,
    instrument,
    market
)

df = chain.get_live_option_chain(
    symbol="NIFTY",
    spot_price=24270.85,
    levels=2
)

print("=" * 80)
print("LIVE OPTION CHAIN")
print("=" * 80)

print(df)