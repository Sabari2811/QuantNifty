from engine.session_manager import SessionManager

session = SessionManager()
breeze = session.connect()

print(breeze.get_portfolio_positions())