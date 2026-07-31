from abc import ABC, abstractmethod

from runtime.runtime_mode import RuntimeMode


class BaseProvider(ABC):
    """
    Base interface for all market data providers.
    """

    # ==========================================================
    # Runtime Mode
    # ==========================================================

    @property
    def runtime_mode(self):

        return RuntimeMode.LIVE

    # ==========================================================
    # Required
    # ==========================================================

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def get_spot_price(self, symbol):
        pass

    @abstractmethod
    def get_historical_data(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_option_chain(self, *args, **kwargs):
        pass

    # ==========================================================
    # Optional
    # ==========================================================

    def get_profile(self):
        raise NotImplementedError

    def place_order(self, *args, **kwargs):
        raise NotImplementedError