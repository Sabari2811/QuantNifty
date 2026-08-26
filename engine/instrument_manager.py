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

        selected = (
            candidates["_EXPIRY_PARSED"]
            .drop_duplicates()
            .sort_values()
            .iloc[0]
        )

        matches = valid[valid["_EXPIRY_PARSED"] == selected]
        return str(matches["EXPIRY_DATE"].iloc[0])

    def get_expiry_dates(self, symbol: str) -> List[str]:

        df = self.get_options(symbol)

        return (
            df["EXPIRY_DATE"]
            .dropna()
            .drop_duplicates()
            .sort_values()
            .tolist()
        )

    def get_nearest_weekly_expiry(self, symbol: str):
        """
        Return the nearest authoritative future weekly expiry.

        For NIFTY, a monthly expiry must never be used as a silent fallback
        when the weekly contract set is missing. If the local F&O master is
        stale and no future NIFTY weekly expiry is present, refresh the
        provider instrument master once and retry before declaring that no
        weekly expiry is available.
        """
        symbol = symbol.upper()
        selected = self._nearest_future_expiry(
            self.get_options(symbol),
            symbol,
        )
        if selected is not None:
            return selected

        # A missing NIFTY weekly expiry is a data-master freshness problem
        # before it is a contract-selection problem. Refresh the authoritative
        # F&O master once instead of silently falling back to a monthly chain.
        if symbol == "NIFTY":
            self.download_instruments("fno")
            selected = self._nearest_future_expiry(
                self.get_options(symbol),
                symbol,
            )
            if selected is not None:
                return selected

        return None

    def get_monthly_expiry(self, symbol: str):

        df = self.get_options(symbol)

        monthly = df[df["EXPIRY_FLAG"] == "M"]

        expiry = (
            monthly["EXPIRY_DATE"]
            .drop_duplicates()
            .sort_values()
            .tolist()
        )

        return expiry[0] if expiry else None

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
            (df["EXPIRY_DATE"] == expiry)
            &
            (df["STRIKE_PRICE"] == float(strike))
            &
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
        Returns SECURITY_ID for supported indices.

        Supports aliases:

            NIFTY
            NIFTY 50

            BANKNIFTY
            BANK NIFTY

            FINNIFTY
            NIFTY FIN SERVICE

            MIDCPNIFTY
            NIFTY MID SELECT
        """

        aliases = {

            "NIFTY": "NIFTY 50",
            "NIFTY50": "NIFTY 50",

            "BANKNIFTY": "BANK NIFTY",
            "NIFTY BANK": "BANK NIFTY",

            "FINNIFTY": "NIFTY FINANCIAL",
            "NIFTY FIN SERVICE": "NIFTY FINANCIAL",

            "MIDCPNIFTY": "NIFTY MIDCAP SEL",
            "NIFTY MID SELECT": "NIFTY MIDCAP SEL"

        }

        lookup = aliases.get(
            index_name.upper(),
            index_name
        )

        df = self.load_index()

        segment = (
            df["SEGMENT"]
            .astype(str)
            .str.upper()
            .str.strip()
        )

        # ------------------------------------------
        # Exact Match
        # ------------------------------------------

        result = df[
            segment == lookup.upper()
        ]

        if not result.empty:

            return int(
                result.iloc[0]["SECURITY_ID"]
            )

        # ------------------------------------------
        # Partial Match
        # ------------------------------------------

        result = df[
            segment.str.contains(
                lookup.upper(),
                regex=False,
                na=False
            )
        ]

        if not result.empty:

            return int(
                result.iloc[0]["SECURITY_ID"]
            )

        print(
            f"Index not found : {index_name}"
        )

        return None
