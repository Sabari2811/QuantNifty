import random

from providers.base_provider import BaseProvider


class MockProvider(BaseProvider):
    """
    Mock Provider

    Used for development/testing without
    connecting to any broker.
    """

    def __init__(self):

        self.connected = False

    # ======================================================
    # CONNECTION
    # ======================================================

    def connect(self):

        self.connected = True

        print("=" * 50)
        print("      CONNECTING TO MOCK PROVIDER")
        print("=" * 50)
        print("✓ Mock Provider Ready")

        return True

    # ======================================================
    # PROFILE
    # ======================================================

    def get_profile(self):

        return {

            "status": "success",

            "data": {

                "broker": "Mock",

                "user": "QuantNifty"

            }

        }

    # ======================================================
    # INDEX QUOTE
    # ======================================================

    def get_index_quote(self, index_name):

        return {

            "live_price": 24050.25,

            "day_change": 102.50,

            "day_change_percentage": 0.42,

            "day_low": 23920,

            "day_high": 24120,

            "day_open": 23980,

            "prev_close": 23947.75

        }

    # ======================================================
    # SPOT PRICE
    # ======================================================

    def get_spot_price(self):

        return 24050.25

    # ======================================================
    # SINGLE QUOTE
    # ======================================================

    def get_quote(self, security_id):

        return {

            "live_price": round(
                random.uniform(40, 300),
                2
            ),

            "open_interest": random.randint(
                10000,
                300000
            ),

            "volume": random.randint(
                1000,
                100000
            )

        }

    # ======================================================
    # MULTIPLE QUOTES
    # ======================================================

    def get_quotes(self, security_ids):

        quotes = {}

        for sid in security_ids:

            quotes[f"NFO_{sid}"] = self.get_quote(sid)

        return quotes

    # ======================================================
    # OPTION CHAIN
    # ======================================================

    def get_option_chain(self):

        return {}

    # ======================================================
    # PLACE ORDER
    # ======================================================

    def place_order(self):

        print("Mock Order Placed")

        return {

            "status": "success",

            "order_id": "MOCK123456"

        }