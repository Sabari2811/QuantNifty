"""Manual ADX smoke script.

This module performs a live-provider call when executed directly. It is not a
pytest regression test; importing it during collection would require broker
credentials and could trigger network activity.
"""

import sys

if "pytest" in sys.modules:
    import pytest

    pytest.skip("live-provider smoke script; run directly when credentials are configured", allow_module_level=True)

from datetime import datetime, timedelta

from providers.indmoney_provider import INDMoneyProvider
from engine.instrument_manager import InstrumentManager
from engine.candle_manager import CandleManager
from analytics.adx_engine import ADXEngine


provider = INDMoneyProvider()
provider.connect()

instrument = InstrumentManager()
instrument.load_index()

security_id = instrument.get_index_security_id("NIFTY 50")

scrip_code = instrument.get_scrip_code(
    "NIDX",
    security_id
)

end = datetime.now()
start = end - timedelta(days=5)

candles = provider.get_historical_data(
    scrip_code=scrip_code,
    interval="5minute",
    start_time=int(start.timestamp() * 1000),
    end_time=int(end.timestamp() * 1000)
)

df = CandleManager().to_dataframe(candles)

result = ADXEngine().calculate(df)

print()
print("=" * 80)
print("ADX ENGINE")
print("=" * 80)
print(result)
