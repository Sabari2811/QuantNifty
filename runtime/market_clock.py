from datetime import datetime, time
from zoneinfo import ZoneInfo


IST = ZoneInfo("Asia/Kolkata")


class MarketClock:
    """NSE equity-derivatives session clock in Asia/Kolkata time."""

    MARKET_OPEN = time(9, 15)
    MARKET_CLOSE = time(15, 40)

    def now(self):
        return datetime.now(IST)

    def _current(self):
        current = self.now()
        if current.tzinfo is None:
            current = current.replace(tzinfo=IST)
        return current.astimezone(IST)

    def is_weekday(self):
        return self._current().weekday() < 5

    def is_market_open(self):
        current = self._current().time()
        return self.is_weekday() and self.MARKET_OPEN <= current <= self.MARKET_CLOSE

    def is_pre_market(self):
        current = self._current()
        return self.is_weekday() and current.time() < self.MARKET_OPEN

    def is_post_market(self):
        current = self._current()
        return (not self.is_weekday()) or current.time() > self.MARKET_CLOSE

    def market_status(self):
        if self.is_market_open():
            return "OPEN"
        if self.is_pre_market():
            return "PRE_MARKET"
        return "CLOSED"
