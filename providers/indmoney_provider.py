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

    # ==========================================================
    # CONNECTION
    # ==========================================================

    def connect(self):

        print("=" * 50)
        print("      CONNECTING TO INDMONEY")
        print("=" * 50)
        print("✓ API Token Loaded")

        return True

    # ==========================================================
    # USER PROFILE
    # ==========================================================

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

    # ==========================================================
    # SINGLE OPTION QUOTE
    # ==========================================================

    def get_quote(self, security_id):

        security_id = int(security_id)

        url = (
            f"{self.base_url}/market/quotes/full"
            f"?scrip-codes=NFO_{security_id}"
        )

        response = requests.get(
            url,
            headers=self.headers,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        if data.get("status") != "success":
            return None

        return data["data"].get(f"NFO_{security_id}")

    # ==========================================================
    # MULTIPLE OPTION QUOTES
    # ==========================================================

    def get_quotes(self, security_ids):

        if not security_ids:
            return {}

        # ---------------------------------------
        # Remove duplicates / None
        # ---------------------------------------

        ids = []

        for sid in security_ids:

            if sid is None:
                continue

            sid = int(sid)

            if sid not in ids:
                ids.append(sid)

        print("\n" + "=" * 70)
        print("OPTION QUOTE REQUEST")
        print("=" * 70)

        print("\nSecurity IDs:")
        print(ids)

        quotes = {}

        # ---------------------------------------
        # INDMONEY occasionally rejects
        # very large requests.
        # Fetch in small batches.
        # ---------------------------------------

        batch_size = 10

        for start in range(0, len(ids), batch_size):

            batch = ids[start:start + batch_size]

            scrip_codes = ",".join(
                f"NFO_{sid}"
                for sid in batch
            )

            url = (
                f"{self.base_url}/market/quotes/full"
                f"?scrip-codes={scrip_codes}"
            )

            print("\n------------------------------------------------")
            print("Request")
            print(url)

            response = requests.get(
                url,
                headers=self.headers,
                timeout=30
            )

            print("Status :", response.status_code)

            if response.status_code != 200:

                print("\nBatch Failed")
                print(response.text)

                continue

            data = response.json()

            if data.get("status") != "success":
                continue

            quotes.update(data["data"])

        print("\nQuotes Received :", len(quotes))

        return quotes

    # ==========================================================
    # INDEX QUOTE USING SECURITY ID
    # ==========================================================

    def get_index_quote_by_id(self, security_id):

        security_id = int(security_id)

        url = (
            f"{self.base_url}/market/quotes/full"
            f"?scrip-codes=NSE_{security_id}"
        )

        print("\n" + "=" * 60)
        print("INDEX QUOTE REQUEST")
        print("=" * 60)

        print("\nURL:")
        print(url)

        response = requests.get(
            url,
            headers=self.headers,
            timeout=30
        )

        print("\nStatus Code:")
        print(response.status_code)

        print("\nResponse:")
        print(response.text)

        response.raise_for_status()

        data = response.json()

        if data.get("status") != "success":
            return None

        return data["data"].get(f"NSE_{security_id}")

    # ==========================================================
    # INDEX QUOTE
    # ==========================================================

    def get_index_quote(self, index_name):

        from engine.instrument_manager import InstrumentManager

        instrument = InstrumentManager()

        security_id = instrument.get_index_security_id(
            index_name
        )

        if security_id is None:
            raise ValueError(
                f"Index not found : {index_name}"
            )

        return self.get_index_quote_by_id(
            security_id
        )

    # ==========================================================
    # PLACE HOLDERS
    # ==========================================================

    def get_spot_price(self):
        raise NotImplementedError()

    def get_option_chain(self):
        raise NotImplementedError()

    def place_order(self):
        raise NotImplementedError()