from engine.session_manager import SessionManager

session = SessionManager()
breeze = session.connect()

print(dir(breeze))