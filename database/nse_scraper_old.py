import requests
import pandas as pd

class NSEDataFetcher:

    def __init__(self):
        self.base_url = "https://www.nseindia.com"
        self.option_chain_url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"

        self.headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br"
        }

        self.session = requests.Session()

    def get_option_chain(self):

        # First visit homepage (important)
        self.session.get(
            self.base_url,
            headers=self.headers,
            timeout=10
        )

        response = self.session.get(
            self.option_chain_url,
            headers=self.headers,
            timeout=10
        )

        response.raise_for_status()

        return response.json()

    def get_dataframe(self):

        data = self.get_option_chain()

        records = []

        for item in data["records"]["data"]:

            strike = item["strikePrice"]

            ce = item.get("CE", {})
            pe = item.get("PE", {})

            records.append({
                "Strike": strike,

                "CE_OI": ce.get("openInterest"),
                "CE_Change_OI": ce.get("changeinOpenInterest"),
                "CE_Volume": ce.get("totalTradedVolume"),
                "CE_IV": ce.get("impliedVolatility"),
                "CE_LTP": ce.get("lastPrice"),

                "PE_OI": pe.get("openInterest"),
                "PE_Change_OI": pe.get("changeinOpenInterest"),
                "PE_Volume": pe.get("totalTradedVolume"),
                "PE_IV": pe.get("impliedVolatility"),
                "PE_LTP": pe.get("lastPrice")
            })

        df = pd.DataFrame(records)

        return df