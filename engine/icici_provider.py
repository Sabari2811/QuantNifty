import pandas as pd


class ICICIProvider:

    def __init__(self, breeze):
        self.breeze = breeze

    def get_spot_price(self):

        response = self.breeze.get_quotes(
            stock_code="NIFTY",
            exchange_code="NSE",
            product_type="cash",
            right="others",
            strike_price="0",
            expiry_date=""
        )

        data = response["Success"][0]

        return {
            "LTP": data["ltp"],
            "OPEN": data["open"],
            "HIGH": data["high"],
            "LOW": data["low"],
            "TIME": data["ltt"]
        }

    def get_option_chain(self,
                         expiry_date,
                         right,
                         strike_price):

        response = self.breeze.get_option_chain_quotes(
            stock_code="NIFTY",
            exchange_code="NFO",
            expiry_date=expiry_date,
            product_type="options",
            right=right,
            strike_price=strike_price
        )

        return response