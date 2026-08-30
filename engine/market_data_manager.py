from providers.indmoney_provider import INDMoneyProvider


class MarketDataManager:
    """
    Market Data Manager

    Responsible for:
        - Spot Price
        - Index Quotes
        - Future Quotes
        - Caching
    """

    def __init__(self, provider: INDMoneyProvider):
        self.provider = provider
        self.cache = {}

    # -------------------------------------------------------
    # Live Spot Quote / Price
    # -------------------------------------------------------

    def get_spot_quote(self, symbol: str):
        symbol = symbol.upper()
        mapping = {
            "NIFTY": "NIFTY 50",
            "BANKNIFTY": "NIFTY BANK",
            "FINNIFTY": "NIFTY FIN SERVICE",
            "MIDCPNIFTY": "NIFTY MID SELECT",
        }
        if symbol not in mapping:
            raise ValueError(f"Unsupported Index : {symbol}")
        return self.provider.get_index_quote(mapping[symbol])

    def get_spot_price(self, symbol: str):
        quote = self.get_spot_quote(symbol)
        if quote is None:
            raise Exception("Unable to fetch live quote.")

        for key in (
            "ltp",
            "LTP",
            "last_price",
            "lastPrice",
            "live_price",
            "close",
        ):
            if key in quote and quote[key] is not None:
                return float(quote[key])

        raise Exception(f"Spot price not found in response: {quote}")

    # -------------------------------------------------------
    # Generic Quote
    # -------------------------------------------------------

    def get_quote(self, symbol):
        return self.provider.get_quote(symbol)

    # -------------------------------------------------------
    # Cache
    # -------------------------------------------------------

    def set_cache(self, key, value):
        self.cache[key] = value

    def get_cache(self, key):
        return self.cache.get(key)
