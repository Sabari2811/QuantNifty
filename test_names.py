from engine.session_manager import SessionManager

session = SessionManager()
breeze = session.connect()

response = breeze.get_names("NIFTY")

print(response)