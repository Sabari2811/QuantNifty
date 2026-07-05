from engine.session_manager import SessionManager

session = SessionManager()
breeze = session.connect()

response = breeze.get_stock_script_list("NFO")

print(response)