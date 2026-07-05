from engine.session_manager import SessionManager

session = SessionManager()
breeze = session.connect()

response = breeze.get_contract_name(
    stock_code="NIFTY",
    exchange_code="NFO",
    product_type="options"
)

print(response)