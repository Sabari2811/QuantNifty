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

        print("=" * 60)
        print("CONNECTING TO INDMONEY")
        print("=" * 60)

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

        ids = []

        for sid in security_ids:

            if sid is None:
                continue

            sid = int(sid)

            if sid not in ids:
                ids.append(sid)

        print()
        print("=" * 70)
        print("OPTION QUOTE REQUEST")
        print("=" * 70)

        print("Security IDs")
        print(ids)

        quotes = {}

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

            print()
            print("--------------------------------------------")
            print("Request")
            print(url)

            response = requests.get(
                url,
                headers=self.headers,
                timeout=30
            )

            print("Status :", response.status_code)

            if response.status_code != 200:

                print("Batch Failed")
                print(response.text)

                continue

            data = response.json()

            if data.get("status") != "success":
                continue

            quotes.update(data["data"])

        print()
        print("Quotes Received :", len(quotes))

        return quotes

    # ==========================================================
    # INDEX QUOTE BY SECURITY ID
    # ==========================================================

    def get_index_quote_by_id(self, security_id):

        security_id = int(security_id)

        url = (
            f"{self.base_url}/market/quotes/full"
            f"?scrip-codes=NIDX_{security_id}"
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

        return data["data"].get(
            f"NIDX_{security_id}"
        )

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
    # EXTRACT PRICE
    # ==========================================================

    def _extract_price(self, quote):

        if quote is None:
            return None

        for key in (

            "live_price",

            "ltp",

            "LTP",

            "last_price",

            "lastPrice",

            "close"

        ):

            value = quote.get(key)

            if value is not None:

                return float(value)

        return None

    # ==========================================================
    # LIVE SPOT PRICE
    # ==========================================================

    def get_spot_price(self, symbol):

        symbol = symbol.upper()

        mapping = {

            "NIFTY": "NIFTY 50",

            "BANKNIFTY": "NIFTY BANK",

            "FINNIFTY": "NIFTY FIN SERVICE",

            "MIDCPNIFTY": "NIFTY MID SELECT"

        }

        if symbol not in mapping:

            raise ValueError(
                f"Unsupported Symbol : {symbol}"
            )

        quote = self.get_index_quote(
            mapping[symbol]
        )

        price = self._extract_price(
            quote
        )

        if price is None:

            raise Exception(

                f"Unable to extract spot price.\nResponse : {quote}"

            )

        return price
    # ==========================================================
    # HISTORICAL DATA
    # ==========================================================

    def get_historical_data(

        self,

        scrip_code,

        interval,

        start_time,

        end_time

    ):

        """
        Fetch historical OHLC candles.

        Example:

            scrip_code = "NIDX_26000"
            interval   = "5"
            start_time = "2026-07-10T09:15:00"
            end_time   = "2026-07-10T15:30:00"

        Supported intervals (per INDStocks API):

            1
            3
            5
            10
            15
            30
            60
            D
            W
            M
        """

        url = (

            f"{self.base_url}/market/historical/{interval}"

        )

        params = {

        "scrip-codes": scrip_code,

        "start_time": start_time,

        "end_time": end_time

        }

        print()
        print("=" * 70)
        print("HISTORICAL DATA REQUEST")
        print("=" * 70)
        print("URL :", url)
        print("Params :", params)

        response = requests.get(

            url,

            headers=self.headers,

            params=params,

            timeout=30

        )

        print("Status :", response.status_code)

        # ------------------------------------------------------
        # HTTP Error
        # ------------------------------------------------------

        if response.status_code != 200:

            print()
            print("=" * 70)
            print("ERROR RESPONSE")
            print("=" * 70)
            print(response.text)

            return []

        # ------------------------------------------------------
        # Parse JSON
        # ------------------------------------------------------

        try:

            data = response.json()

        except Exception:

            print()
            print("=" * 70)
            print("INVALID JSON")
            print("=" * 70)
            print(response.text)

            return []
        # ------------------------------------------------------
        # Parse JSON
        # ------------------------------------------------------

        try:

            data = response.json()

        except Exception:

            print()
            print("=" * 70)
            print("INVALID JSON")
            print("=" * 70)
            print(response.text)

            return []

        # ------------------------------------------------------
        # Success Check
        # ------------------------------------------------------

        if not data.get("success", False):

            print()
            print("=" * 70)
            print("API ERROR")
            print("=" * 70)
            print(data)

            return []

        # ------------------------------------------------------
        # Validate Response
        # ------------------------------------------------------

        if "data" not in data:

            return []

        if scrip_code not in data["data"]:

            return []

        if "candles" not in data["data"][scrip_code]:

            return []

        candles = data["data"][scrip_code]["candles"]

        print()
        print("Candles Returned :", len(candles))

        return candles
    # ==========================================================
    # OPTION CHAIN
    # ==========================================================

    def get_option_chain(self, *args, **kwargs):
        """
        Not required.

        QuantNifty builds the option chain through
        OptionChainManager using get_quotes().
        """
        raise NotImplementedError(
            "Use OptionChainManager.get_live_option_chain()"
        )

    # ==========================================================
    # PLACE ORDER
    # ==========================================================

    def place_order(self, *args, **kwargs):

        raise NotImplementedError(
            "Order placement will be implemented in Sprint 38."
        )