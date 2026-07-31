from datetime import datetime, time


class MarketClock:

    MARKET_OPEN = time(9, 15)
    MARKET_CLOSE = time(15, 30)

    def now(self):
        return datetime.now()

    def is_market_open(self):

        current = self.now().time()

        return self.MARKET_OPEN <= current <= self.MARKET_CLOSE

    def is_pre_market(self):

        return self.now().time() < self.MARKET_OPEN

    def is_post_market(self):

        return self.now().time() > self.MARKET_CLOSE

    def market_status(self):

        if self.is_pre_market():
            return "PRE_MARKET"

        if self.is_market_open():
            return "OPEN"

        return "CLOSED"