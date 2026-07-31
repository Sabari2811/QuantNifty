from abc import ABC, abstractmethod


class BaseStrategy(ABC):
    """
    Strategy modifies the institutional score.

    It never calculates the base score.
    """

    @abstractmethod
    def adjust(self, score, market):

        pass