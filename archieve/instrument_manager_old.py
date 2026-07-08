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

    # ----------------------------------------------------
    # Download Instrument Master
    # ----------------------------------------------------
    def download_instruments(self, source):
        """
        Downloads instrument master CSV.

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

    # ----------------------------------------------------
    # Load Instrument CSV
    # ----------------------------------------------------
    def load_instruments(self, source):
        """
        Loads instrument CSV into a Pandas DataFrame.

        source:
            index
            equity
            fno
        """

        filename = os.path.join(
            self.save_folder,
            f"{source}.csv"
        )

        if not os.path.exists(filename):
            raise FileNotFoundError(
                f"{filename} not found.\nRun download_instruments() first."
            )

        df = pd.read_csv(filename)

        print(f"{source} instruments loaded successfully.")
        print(f"Total Records : {len(df)}")

        return df

    # ----------------------------------------------------
    # Search Instrument
    # ----------------------------------------------------
    def search_symbol(self, source, keyword):
        """
        Search any instrument by keyword.

        Example:
            search_symbol("index", "NIFTY")
            search_symbol("equity", "RELIANCE")
        """

        df = self.load_instruments(source)

        keyword = keyword.upper()

        result = df[
            df.astype(str)
              .apply(lambda col: col.str.upper().str.contains(keyword, na=False))
              .any(axis=1)
        ]

        print(f"\nMatching Records : {len(result)}")

        return result

    # ----------------------------------------------------
    # Display CSV Information
    # ----------------------------------------------------
    def show_columns(self, source):
        """
        Prints all column names of a downloaded CSV.
        Useful for understanding the data structure.
        """

        df = self.load_instruments(source)

        print("\nColumns:\n")

        for column in df.columns:
            print(column)

        return df.columns