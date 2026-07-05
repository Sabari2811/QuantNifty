from engine.session_manager import SessionManager
from engine.icici_provider import ICICIProvider

print("=" * 50)
print("       NIFTY SIGNAL ENGINE")
print("=" * 50)

session = SessionManager()
breeze = session.connect()

provider = ICICIProvider(breeze)

print("✅ Provider Initialized Successfully")