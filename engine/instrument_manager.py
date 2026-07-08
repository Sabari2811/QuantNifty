import os
from typing import Dict, List

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()


class InstrumentManager:
    """
    Instrument Manager

    Responsibilities
    ----------------
    - Download instrument masters
    - Cache DataFrames
    - Search instruments
    - Lookup option contracts
    - Expiry lookup
    - Security ID lookup
    """

    BASE_URL = "https://api.indstocks.com"

    def __init__(self):

        self.token = os.getenv("INDSTOCKS_API_TOKEN")

        if not self.token:
            raise Exception("INDSTOCKS_API_TOKEN not found.")

        self.headers = {
            "Authorization": self.token,
            "Content-Type": "application/json"
        }

        self.save_folder = "data/instruments"

        os.makedirs(self.save_folder, exist_ok=True)

        # In-memory cache
        self.cache: Dict[str, pd.DataFrame] = {}

    # ======================================================
    # DOWNLOAD
    # ======================================================

    def download_instruments(self, source: str):

        print(f"\nDownloading {source} instruments...")

        response = requests.get(
            f"{self.BASE_URL}/market/instruments",
            headers=self.headers,
            params={"source": source},
            timeout=60
        )

        response.raise_for_status()

        filename = os.path.join(
            self.save_folder,
            f"{source}.csv"
        )

        with open(filename, "wb") as f:
            f.write(response.content)

        print(f"Saved : {filename}")

        self.cache.pop(source, None)

    # ======================================================
    # LOAD
    # ======================================================

    def load(self, source: str) -> pd.DataFrame:

        if source in self.cache:
            return self.cache[source]

        filename = os.path.join(
            self.save_folder,
            f"{source}.csv"
        )

        if not os.path.exists(filename):
            raise FileNotFoundError(filename)

        df = pd.read_csv(filename)

        self.cache[source] = df

        print(f"{source.upper()} loaded ({len(df)} records).")

        return df

    # ======================================================
    # COMPATIBILITY METHODS
    # ======================================================

    def load_fno(self):
        return self.load("fno")

    def load_index(self):
        return self.load("index")

    def load_equity(self):
        return self.load("equity")

    # ======================================================
    # PUBLIC
    # ======================================================

    def get_dataframe(self, source: str):

        return self.load(source)

    def stats(self, source: str):

        df = self.load(source)

        print("\nRows :", len(df))
        print("Columns :", len(df.columns))

    def columns(self, source: str):

        df = self.load(source)

        print()

        for c in df.columns:
            print(c)

    # ======================================================
    # SEARCH
    # ======================================================

    def search(self, source: str, keyword: str):

        df = self.load(source)

        keyword = keyword.upper()

        return df[
            df.astype(str)
            .apply(lambda c: c.str.upper().str.contains(keyword, na=False))
            .any(axis=1)
        ]

    # ======================================================
    # OPTIONS
    # ======================================================

    def get_options(self, symbol: str) -> pd.DataFrame:

        df = self.load("fno")

        symbol = symbol.upper()

        first_token = (
            df["TRADING_SYMBOL"]
            .astype(str)
            .str.split("-")
            .str[0]
            .str.upper()
        )

        return df[first_token == symbol].copy()

    # ======================================================
    # EXPIRY
    # ======================================================

    def get_expiry_dates(self, symbol: str) -> List[str]:

        df = self.get_options(symbol)

        expiry = (
            df["EXPIRY_DATE"]
            .dropna()
            .drop_duplicates()
            .sort_values()
            .tolist()
        )

        return expiry

    def get_nearest_weekly_expiry(self, symbol: str):

        df = self.get_options(symbol)

        weekly = df[df["EXPIRY_FLAG"] == "W"]

        expiry = (
            weekly["EXPIRY_DATE"]
            .drop_duplicates()
            .sort_values()
            .tolist()
        )

        if not expiry:
            return None

        return expiry[0]

    def get_monthly_expiry(self, symbol: str):

        df = self.get_options(symbol)

        monthly = df[df["EXPIRY_FLAG"] == "M"]

        expiry = (
            monthly["EXPIRY_DATE"]
            .drop_duplicates()
            .sort_values()
            .tolist()
        )

        if not expiry:
            return None

        return expiry[0]

    # ======================================================
    # OPTION LOOKUP
    # ======================================================

    def get_option(
        self,
        symbol: str,
        expiry: str,
        strike: float,
        option_type: str
    ):

        df = self.get_options(symbol)

        result = df[
            (df["EXPIRY_DATE"] == expiry) &
            (df["STRIKE_PRICE"] == float(strike)) &
            (df["OPTION_TYPE"] == option_type.upper())
        ]

        if result.empty:
            return None

        return result.iloc[0]

    # ======================================================
    # SECURITY ID
    # ======================================================

    def get_security_id(
        self,
        symbol: str,
        expiry: str,
        strike: float,
        option_type: str
    ):

        option = self.get_option(
            symbol,
            expiry,
            strike,
            option_type
        )

        if option is None:
            return None

        return int(option["SECURITY_ID"])

    # ======================================================
    # LOT SIZE
    # ======================================================

    def get_lot_size(self, symbol: str):

        df = self.get_options(symbol)

        if df.empty:
            return None

        return int(df.iloc[0]["LOT_UNITS"])
    # ======================================================
    # INDEX SECURITY ID
    # ======================================================

    def get_index_security_id(self, index_name: str):
        """
        Returns SECURITY_ID for an index.

        Example:
            NIFTY 50
            NIFTY BANK
            India VIX
        """

        df = self.load_index()

        result = df[
            df["SEGMENT"]
            .astype(str)
            .str.upper()
            == index_name.upper()
        ]

        if result.empty:
            return None

        return int(result.iloc[0]["SECURITY_ID"])