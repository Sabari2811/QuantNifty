from engine.session_manager import SessionManager

session = SessionManager()
breeze = session.connect()

response = breeze.get_quotes(
    stock_code="NIFTY",
    exchange_code="NFO",
    product_type="futures",
    expiry_date="2026-07-09T06:00:00.000Z",
    right="others",
    strike_price="0"
)

print(response)