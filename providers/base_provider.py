from abc import ABC, abstractmethod


class BaseProvider(ABC):

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def get_profile(self):
        pass

    @abstractmethod
    def get_spot_price(self):
        pass

    @abstractmethod
    def get_option_chain(self):
        pass

    @abstractmethod
    def place_order(self):
        pass