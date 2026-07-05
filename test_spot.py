from engine.session_manager import SessionManager
from engine.icici_provider import ICICIProvider

session = SessionManager()
breeze = session.connect()

provider = ICICIProvider(breeze)

spot = provider.get_spot_price()

print()

print("========= NIFTY LIVE =========")

for key, value in spot.items():
    print(f"{key:<12}: {value}")