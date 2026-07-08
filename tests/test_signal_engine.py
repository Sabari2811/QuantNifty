from analytics.analytics_pipeline import AnalyticsPipeline

from providers.indmoney_provider import INDMoneyProvider

from engine.instrument_manager import InstrumentManager
from engine.market_data_manager import MarketDataManager
from engine.strike_selector import StrikeSelector
from engine.option_chain_manager import OptionChainManager
from engine.live_greeks_engine import LiveGreeksEngine


# ==========================================================
# CONNECT
# ==========================================================

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

# ==========================================================
# LIVE MARKET DATA
# ==========================================================

spot = market.get_spot_price("NIFTY")

print()
print("=" * 70)
print("LIVE MARKET")
print("=" * 70)
print(f"Spot Price : {spot}")

expiry = instrument.get_nearest_weekly_expiry("NIFTY")

print(f"Expiry     : {expiry}")

# ==========================================================
# OPTION CHAIN
# ==========================================================

option_chain = chain.get_live_option_chain(
    symbol="NIFTY",
    spot_price=spot,
    levels=5
)

# ==========================================================
# GREEKS
# ==========================================================

greeks = LiveGreeksEngine()

df = greeks.calculate_chain_greeks(
    option_chain,
    spot,
    expiry
)

print()
print("=" * 70)
print("OPTION GREEKS")
print("=" * 70)

print(df)

# ==========================================================
# ANALYTICS PIPELINE
# ==========================================================

pipeline = AnalyticsPipeline()

result = pipeline.run(
    greeks,
    df,
    spot
)

# ==========================================================
# RESULTS
# ==========================================================

print()
print("=" * 70)
print("ANALYTICS PIPELINE")
print("=" * 70)

for key, value in result.items():

    print(f"\n{key.upper()}")

    if isinstance(value, dict):

        for k, v in value.items():
            print(f"  {k:30} : {v}")

    else:
        print(value)

print()
print("=" * 70)
print("PIPELINE COMPLETED")
print("=" * 70)