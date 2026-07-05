from breeze_connect import BreezeConnect

from settings.settings import (
    BREEZE_API_KEY,
    BREEZE_SECRET_KEY,
    API_SESSION
)


class SessionManager:
    """
    Handles Breeze API authentication.
    """

    def __init__(self):
        self.breeze = BreezeConnect(api_key=BREEZE_API_KEY)

    def connect(self):
        try:
            self.breeze.generate_session(
                api_secret=BREEZE_SECRET_KEY,
                session_token=API_SESSION
            )

            print("✅ Breeze Login Successful")

            return self.breeze

        except Exception as e:
            print(f"❌ Login Failed : {e}")
            raise