from providers.indmoney_provider import INDMoneyProvider

from engine.instrument_manager import InstrumentManager
from engine.market_data_manager import MarketDataManager
from engine.strike_selector import StrikeSelector
from engine.option_chain_manager import OptionChainManager
from engine.live_greeks_engine import LiveGreeksEngine

from analytics.exposure.delta_exposure_engine import DeltaExposureEngine


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

engine = DeltaExposureEngine()

result = engine.calculate(
    df,
    spot
)

print()

print("=" * 60)
print("DELTA EXPOSURE")
print("=" * 60)

print(
    result[
        [
            "Strike",
            "CALL_DEX",
            "PUT_DEX",
            "NET_DEX"
        ]
    ]
)

print()

print(
    "TOTAL DEX :",
    round(engine.total_dex(result), 2)
)