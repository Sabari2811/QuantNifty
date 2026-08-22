from abc import ABC, abstractmethod


class BaseStrategy(ABC):
    """
    Strategy modifies the institutional score.

    It never calculates the base score.

    Every strategy exposes an explicit canonical identity
    so downstream decision and intelligence layers do not
    need to infer identity from Python class names.
    """

    @property
    @abstractmethod
    def name(self):
        """
        Canonical strategy identity.
        """
        pass

    @abstractmethod
    def adjust(self, score, market):
        """
        Apply strategy-specific adjustment to the score.

        Returns:
            tuple:
                adjusted_score,
                reasons
        """
        pass