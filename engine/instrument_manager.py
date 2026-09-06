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
        # Credential presence is required only for provider downloads. Local
        # master loading/search and deterministic runtime tests must remain
        # usable without broker credentials.
        self.token = os.getenv("INDSTOCKS_API_TOKEN")
        self.headers = {
            "Authorization": self.token,
            "Content-Type": "application/json",
        }

        self.save_folder = "data/instruments"
        os.makedirs(self.save_folder, exist_ok=True)

        # In-memory cache
        self.cache: Dict[str, pd.DataFrame] = {}

    # ======================================================
    # DOWNLOAD
    # ======================================================

    def download_instruments(self, source: str):
        if not self.token:
            raise RuntimeError("INDSTOCKS_API_TOKEN is required to download instruments.")

        print(f"\nDownloading {source} instruments...")

        response = requests.get(
            f"{self.BASE_URL}/market/instruments",
            headers=self.headers,
            params={"source": source},
            timeout=60,
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
            .apply(
                lambda c: c.str.upper().str.contains(
                    keyword,
                    na=False
                )
            )
            .any(axis=1)
        ]

    # ======================================================
    # SCRIP CODE
    # ======================================================

    def get_scrip_code(
        self,
        exchange,
        security_id
    ):
        exchange = str(exchange).upper()
        security_id = int(security_id)
        return f"{exchange}_{security_id}"

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

    @staticmethod
    def _nearest_future_expiry(df: pd.DataFrame, symbol: str):
        """Select the authoritative nearest future expiry from one master."""
        if df.empty:
            return None

        expiry_dates = pd.to_datetime(
            df["EXPIRY_DATE"],
            errors="coerce",
        )

        valid = df.loc[expiry_dates.notna()].copy()
        if valid.empty:
            return None

        valid["_EXPIRY_PARSED"] = pd.to_datetime(
            valid["EXPIRY_DATE"],
            errors="coerce",
        )

        now = pd.Timestamp.now()
        future = valid[valid["_EXPIRY_PARSED"] > now].copy()
        if future.empty:
            return None

        weekly = future[
            future["EXPIRY_FLAG"]
            .astype(str)
            .str.upper()
            .eq("W")
        ].copy()

        # NIFTY 50 is the only supported symbol here with weekly index
        # options. Never silently substitute a monthly expiry when the
        # weekly contract set is absent: that would produce a complete but
        # semantically wrong live option chain.
        if symbol.upper() == "NIFTY":
            if weekly.empty:
                return None
            candidates = weekly
        elif not weekly.empty:
            candidates = weekly
        else:
            candidates = future

        return candidates.sort_values("_EXPIRY_PARSED").iloc[0]["EXPIRY_DATE"]
