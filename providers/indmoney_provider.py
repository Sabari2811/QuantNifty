import os
import requests
from dotenv import load_dotenv

from providers.base_provider import BaseProvider

load_dotenv()


class INDMoneyProvider(BaseProvider):

    def __init__(self):
        self.base_url = "https://api.indstocks.com"

        self.token = os.getenv("INDSTOCKS_API_TOKEN")

        if not self.token:
            raise Exception("INDSTOCKS_API_TOKEN not found in .env")

        self.headers = {
            "Authorization": self.token,
            "Content-Type": "application/json"
        }

    def connect(self):
        print("=" * 50)
        print("      CONNECTING TO INDMONEY")
        print("=" * 50)
        print("✓ API Token Loaded")
        return True

    def get_profile(self):
        url = f"{self.base_url}/user/profile"

        response = requests.get(
            url,
            headers=self.headers,
            timeout=30
        )

        print(f"Status Code : {response.status_code}")

        try:
            return response.json()
        except Exception:
            return response.text

    def get_spot_price(self):
        raise NotImplementedError("Will implement later.")

    def get_option_chain(self):
        raise NotImplementedError("Will implement later.")

    def place_order(self):
        raise NotImplementedError("Will implement later.")