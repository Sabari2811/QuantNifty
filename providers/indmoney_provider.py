import os
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

from providers.base_provider import BaseProvider
from core.logger import logger

load_dotenv()


class INDMoneyProvider(BaseProvider):
    def __init__(self):
        self.base_url = "https://api.indstocks.com"
        self.token = os.getenv("INDSTOCKS_API_TOKEN")
        if not self.token:
            raise Exception("INDSTOCKS_API_TOKEN not found in .env")
        self.headers = {"Authorization": self.token, "Content-Type": "application/json"}

    def connect(self):
        logger.info("CONNECTING TO INDMONEY")
        logger.info("INDMoney API Token Loaded")
        return True

    @staticmethod
    def _normalise_quote(quote):
        """Preserve the provider quote and expose common timestamp/bid/ask aliases.

        No market value is synthesized.  These aliases are metadata only and
        are used by provenance/freshness consumers when the provider supplies
        them under a supported name.
        """
        if not isinstance(quote, dict):
            return quote
        result = dict(quote)
        timestamp_keys = (
            "quote_timestamp", "timestamp", "exchange_timestamp",
            "exchangeTimestamp", "last_trade_time", "lastTradeTime",
            "updated_at", "updatedAt", "time",
        )
        for key in timestamp_keys:
            value = quote.get(key)
            if value is not None:
                result["provider_timestamp"] = value
                break
        for canonical, keys in {
            "bid_price": ("bid_price", "bidPrice", "best_bid", "bestBid", "buy_price"),
            "ask_price": ("ask_price", "askPrice", "best_ask", "bestAsk", "sell_price"),
        }.items():
            for key in keys:
                value = quote.get(key)
                if value is not None:
                    result[canonical] = value
                    break
        return result

    def get_quote(self, security_id):
        security_id = int(security_id)
        url = f"{self.base_url}/market/quotes/full?scrip-codes=NFO_{security_id}"
        response = requests.get(url, headers=self.headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        if data.get("status") != "success":
            return None
        quote = data["data"].get(f"NFO_{security_id}")
        return self._normalise_quote(quote)

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
        logger.info("OPTION QUOTE REQUEST | security_ids=%s", ids)
        quotes = {}
        batch_size = 10
        for start in range(0, len(ids), batch_size):
            batch = ids[start:start + batch_size]
            scrip_codes = ",".join(f"NFO_{sid}" for sid in batch)
            url = f"{self.base_url}/market/quotes/full?scrip-codes={scrip_codes}"
            logger.info("OPTION QUOTE REQUEST | batch=%s | url=%s", batch, url)
            response = requests.get(url, headers=self.headers, timeout=30)
            logger.info("OPTION QUOTE RESPONSE | status=%s", response.status_code)
            if response.status_code != 200:
                logger.error("OPTION QUOTE BATCH FAILED | status=%s | response=%s", response.status_code, response.text)
                continue
            data = response.json()
            if data.get("status") != "success":
                logger.warning("OPTION QUOTE API FAILURE | response=%s", data)
                continue
            quotes.update({key: self._normalise_quote(value) for key, value in data["data"].items()})
        logger.info("OPTION QUOTE COMPLETE | quotes_received=%s", len(quotes))
        return quotes

    def get_index_quote_by_id(self, security_id):
        security_id = int(security_id)
        url = f"{self.base_url}/market/quotes/full?scrip-codes=NIDX_{security_id}"
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.error("INDEX QUOTE REQUEST FAILED | security_id=%s | error=%s", security_id, exc)
            return None
        try:
            data = response.json()
        except ValueError:
            logger.error("INDEX QUOTE INVALID JSON | security_id=%s", security_id)
            return None
        if data.get("status") != "success":
            logger.error("INDEX QUOTE API FAILURE | security_id=%s | status=%s", security_id, data.get("status"))
            return None
        quote = data.get("data", {}).get(f"NIDX_{security_id}")
        return self._normalise_quote(quote)

    def get_index_quote(self, index_name):
        from engine.instrument_manager import InstrumentManager
        instrument = InstrumentManager()
        security_id = instrument.get_index_security_id(index_name)
        if security_id is None:
            raise ValueError(f"Index not found : {index_name}")
        return self.get_index_quote_by_id(security_id)

    def _extract_price(self, quote):
        if quote is None:
            return None
        for key in ("live_price", "ltp", "LTP", "last_price", "lastPrice", "close"):
            value = quote.get(key)
            if value is not None:
                return float(value)
        return None

    def get_spot_price(self, symbol):
        symbol = symbol.upper()
        mapping = {"NIFTY": "NIFTY 50", "BANKNIFTY": "NIFTY BANK", "FINNIFTY": "NIFTY FIN SERVICE", "MIDCPNIFTY": "NIFTY MID SELECT"}
        if symbol not in mapping:
            raise ValueError(f"Unsupported Symbol : {symbol}")
        quote = self.get_index_quote(mapping[symbol])
        price = self._extract_price(quote)
        if price is None:
            raise Exception(f"Unable to extract spot price.\nResponse : {quote}")
        return price

    def get_historical_data(self, scrip_code, interval, start_time, end_time):
        url = f"{self.base_url}/market/historical/{interval}"
        params = {"scrip-codes": scrip_code, "start_time": start_time, "end_time": end_time}
        logger.info("HISTORICAL DATA REQUEST | url=%s | params=%s", url, params)
        response = requests.get(url, headers=self.headers, params=params, timeout=30)
        logger.info("HISTORICAL DATA RESPONSE | status=%s", response.status_code)
        if response.status_code != 200:
            logger.error("HISTORICAL DATA HTTP ERROR | status=%s | response=%s", response.status_code, response.text)
            return []
        try:
            data = response.json()
        except Exception:
            logger.exception("HISTORICAL DATA INVALID JSON")
            return []
        if not data.get("success", False) or "data" not in data or scrip_code not in data["data"]:
            return []
        candles = data["data"][scrip_code].get("candles", [])
        logger.info("HISTORICAL DATA COMPLETE | candles=%s", len(candles))
        return candles

    def get_option_chain(self, *args, **kwargs):
        raise NotImplementedError("Use OptionChainManager.get_live_option_chain()")

    def place_order(self, *args, **kwargs):
        raise NotImplementedError("Order placement will be implemented in Sprint 38.")
