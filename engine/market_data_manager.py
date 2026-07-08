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
    # Live Spot Price
    # -------------------------------------------------------

    def get_spot_price(self, symbol: str):

        symbol = symbol.upper()

        if symbol == "NIFTY":

            quote = self.provider.get_index_quote("NIFTY 50")

        elif symbol == "BANKNIFTY":

            quote = self.provider.get_index_quote("NIFTY BANK")

        elif symbol == "FINNIFTY":

            quote = self.provider.get_index_quote("NIFTY FIN SERVICE")

        elif symbol == "MIDCPNIFTY":

            quote = self.provider.get_index_quote("NIFTY MID SELECT")

        else:

            raise ValueError(f"Unsupported Index : {symbol}")

        if quote is None:

            raise Exception("Unable to fetch live quote.")

        # ----------------------------
        # Try common response keys
        # ----------------------------

        for key in (
            "ltp",
            "LTP",
            "last_price",
            "lastPrice",
            "live_price",
            "close",
        ):

            if key in quote:

                return float(quote[key])

        raise Exception(
            f"Spot price not found in response: {quote}"
        )

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