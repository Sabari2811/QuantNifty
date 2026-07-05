import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


class InstrumentManager:

    BASE_URL = "https://api.indstocks.com"

    def __init__(self):

        self.token = os.getenv("INDSTOCKS_API_TOKEN")

        if not self.token:
            raise Exception("INDSTOCKS_API_TOKEN not found")

        self.headers = {
            "Authorization": self.token,
            "Content-Type": "application/json"
        }

        self.save_folder = "data/instruments"

        os.makedirs(self.save_folder, exist_ok=True)

    def download_instruments(self, source):

        """
        source:
            index
            equity
            fno
        """

        print(f"\nDownloading {source} instruments...")

        url = f"{self.BASE_URL}/market/instruments"

        params = {
            "source": source
        }

        response = requests.get(
            url,
            headers=self.headers,
            params=params,
            timeout=60
        )

        print("Status :", response.status_code)

        if response.status_code != 200:
            print(response.text)
            return

        filename = os.path.join(
            self.save_folder,
            f"{source}.csv"
        )

        with open(filename, "wb") as f:
            f.write(response.content)

        print(f"Saved : {filename}")