import os

import requests
from dotenv import load_dotenv

from providers.base_provider import BaseProvider
from core.logger import logger


load_dotenv()


class INDMoneyProvider(BaseProvider):

    def __init__(self):

        self.base_url = "https://api.indstocks.com"

        self.token = os.getenv(
            "INDSTOCKS_API_TOKEN"
        )

        if not self.token:

            raise Exception(
                "INDSTOCKS_API_TOKEN not found in .env"
            )

        self.headers = {
            "Authorization": self.token,
            "Content-Type": "application/json"
        }

    # ==========================================================
    # CONNECTION
    # ==========================================================

    def connect(self):

        logger.info(
            "CONNECTING TO INDMONEY"
        )

        logger.info(
            "INDMoney API Token Loaded"
        )

        return True

    # ==========================================================
    # USER PROFILE
    # ==========================================================

    def get_profile(self):

        url = (
            f"{self.base_url}/user/profile"
        )

        response = requests.get(
            url,
            headers=self.headers,
            timeout=30
        )

        logger.info(
            "INDMoney PROFILE | status=%s",
            response.status_code,
        )

        try:

            return response.json()

        except Exception:

            return response.text

    # ==========================================================
    # SINGLE OPTION QUOTE
    # ==========================================================

    def get_quote(
        self,
        security_id
    ):

        security_id = int(
            security_id
        )

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

        return data["data"].get(
            f"NFO_{security_id}"
        )

    # ==========================================================
    # MULTIPLE OPTION QUOTES
    # ==========================================================

    def get_quotes(
        self,
        security_ids
    ):

        if not security_ids:

            return {}

        ids = []

        for sid in security_ids:

            if sid is None:

                continue

            sid = int(sid)

            if sid not in ids:

                ids.append(sid)

        logger.info(
            "OPTION QUOTE REQUEST | security_ids=%s",
            ids,
        )

        quotes = {}

        batch_size = 10

        for start in range(
            0,
            len(ids),
            batch_size
        ):

            batch = ids[
                start:start + batch_size
            ]

            scrip_codes = ",".join(
                f"NFO_{sid}"
                for sid in batch
            )

            url = (
                f"{self.base_url}/market/quotes/full"
                f"?scrip-codes={scrip_codes}"
            )

            logger.info(
                "OPTION QUOTE REQUEST | batch=%s | url=%s",
                batch,
                url,
            )

            response = requests.get(
                url,
                headers=self.headers,
                timeout=30
            )

            logger.info(
                "OPTION QUOTE RESPONSE | status=%s",
                response.status_code,
            )

            if response.status_code != 200:

                logger.error(
                    "OPTION QUOTE BATCH FAILED | status=%s | response=%s",
                    response.status_code,
                    response.text,
                )

                continue

            data = response.json()

            if data.get("status") != "success":

                logger.warning(
                    "OPTION QUOTE API FAILURE | response=%s",
                    data,
                )

                continue

            quotes.update(
                data["data"]
            )

        logger.info(
            "OPTION QUOTE COMPLETE | quotes_received=%s",
            len(quotes),
        )

        return quotes

    # ==========================================================
    # INDEX QUOTE BY SECURITY ID
    # ==========================================================

    def get_index_quote_by_id(
        self,
        security_id
    ):

        security_id = int(
            security_id
        )

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

    def get_index_quote(
        self,
        index_name
    ):

        from engine.instrument_manager import (
            InstrumentManager
        )

        instrument = InstrumentManager()

        security_id = (
            instrument.get_index_security_id(
                index_name
            )
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

    def _extract_price(
        self,
        quote
    ):

        if quote is None:

            return None

        for key in (
            "live_price",
            "ltp",
            "LTP",
            "last_price",
            "lastPrice",
            "close",
        ):

            value = quote.get(
                key
            )

            if value is not None:

                return float(value)

        return None

    # ==========================================================
    # LIVE SPOT PRICE
    # ==========================================================

    def get_spot_price(
        self,
        symbol
    ):

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
                f"Unable to extract spot price.\n"
                f"Response : {quote}"
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
        """

        url = (
            f"{self.base_url}/market/historical/{interval}"
        )

        params = {
            "scrip-codes": scrip_code,
            "start_time": start_time,
            "end_time": end_time
        }

        logger.info(
            "HISTORICAL DATA REQUEST | url=%s | params=%s",
            url,
            params,
        )

        response = requests.get(
            url,
            headers=self.headers,
            params=params,
            timeout=30
        )

        logger.info(
            "HISTORICAL DATA RESPONSE | status=%s",
            response.status_code,
        )

        # ------------------------------------------------------
        # HTTP Error
        # ------------------------------------------------------

        if response.status_code != 200:

            logger.error(
                "HISTORICAL DATA HTTP ERROR | status=%s | response=%s",
                response.status_code,
                response.text,
            )

            return []

        # ------------------------------------------------------
        # Parse JSON
        # ------------------------------------------------------

        try:

            data = response.json()

        except Exception:

            logger.exception(
                "HISTORICAL DATA INVALID JSON"
            )

            logger.debug(
                "HISTORICAL DATA RAW RESPONSE | %s",
                response.text,
            )

            return []

        # ------------------------------------------------------
        # Success Check
        # ------------------------------------------------------

        if not data.get(
            "success",
            False
        ):

            logger.error(
                "HISTORICAL DATA API ERROR | response=%s",
                data,
            )

            return []

        # ------------------------------------------------------
        # Validate Response
        # ------------------------------------------------------

        if "data" not in data:

            return []

        if scrip_code not in data["data"]:

            return []

        if (
            "candles"
            not in data["data"][scrip_code]
        ):

            return []

        candles = data[
            "data"
        ][scrip_code]["candles"]

        logger.info(
            "HISTORICAL DATA COMPLETE | candles=%s",
            len(candles),
        )

        return candles

    # ==========================================================
    # OPTION CHAIN
    # ==========================================================

    def get_option_chain(
        self,
        *args,
        **kwargs
    ):
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

    def place_order(
        self,
        *args,
        **kwargs
    ):

        raise NotImplementedError(
            "Order placement will be implemented in Sprint 38."
        )