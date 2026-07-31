from abc import ABC, abstractmethod


class BaseStrategy(ABC):
    """
    Base class for all QuantNifty strategies.

    Every strategy must implement the same interface.
    """

    @abstractmethod
    def on_market_update(self, market_context):
        """
        Called whenever the market updates.

        Parameters
        ----------
        market_context

            Complete market snapshot.

        Returns
        -------

        Decision | None
        """

        raise NotImplementedError()