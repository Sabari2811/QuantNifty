from engine.session_manager import SessionManager
from engine.icici_provider import ICICIProvider

session = SessionManager()
breeze = session.connect()

provider = ICICIProvider(breeze)

for right in ["call", "put"]:
    print(f"\nTesting {right.upper()}...\n")

    response = provider.get_option_chain(
        expiry_date="2026-07-09T06:00:00.000Z",
        right=right,
        strike_price="24250"
    )

    print(response)